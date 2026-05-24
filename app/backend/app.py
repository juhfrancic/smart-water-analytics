import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pyodbc
from databricks import sql as databricks_sql
from datetime import datetime
import uuid

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, 'templates'),
    static_folder=os.path.join(FRONTEND_DIR, 'static'),
    static_url_path='/static'
)
CORS(app)

db_user     = os.getenv("SQLSERVER_USER",     "sa")
db_password = os.getenv("SQLSERVER_PASSWORD", "")

DBR_HOST      = os.getenv("DATABRICKS_HOST")
DBR_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DBR_TOKEN     = os.getenv("DATABRICKS_TOKEN")
DBR_CATALOG   = os.getenv("DATABRICKS_CATALOG", "workspace")
DBR_SCHEMA    = os.getenv("DATABRICKS_SCHEMA",  "gold")

SQL_SERVER_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=saneamento_db;"
    f"UID={db_user};"
    f"PWD={db_password};"
    "TrustServerCertificate=yes;"
)

def executar_query(query, params=(), retorno_dados=True):
    try:
        conn   = pyodbc.connect(SQL_SERVER_CONN)
        cursor = conn.cursor()
        cursor.execute(query, params)
        resultado = []
        if retorno_dados and cursor.description:
            colunas   = [desc[0] for desc in cursor.description]
            resultado = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        else:
            conn.commit()
        conn.close()
        return resultado
    except Exception as e:
        print(f"[ERRO SQL Server] {e}")
        return [] if retorno_dados else False

def dbr(query):
    try:
        with databricks_sql.connect(
            server_hostname = DBR_HOST,
            http_path       = DBR_HTTP_PATH,
            access_token    = DBR_TOKEN,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                colunas = [d[0] for d in cursor.description]
                return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f"[ERRO Databricks] {e}")
        return []

def tb(nome):
    return f"{DBR_CATALOG}.{DBR_SCHEMA}.{nome}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/pontos', methods=['GET'])
def listar_pontos():
    pontos = dbr(f"""
        SELECT
            p.ponto_rede_id,
            p.nome_ponto,
            p.tipo_ponto,
            p.zona_pressao,
            p.latitude,
            p.longitude,
            p.status_operacional,
            p.nivel_criticidade,
            s.nome_setor,
            l.pressao_mpa    AS pressao_atual,
            l.vazao_l_min    AS vazao_atual,
            l.nivel_reservatorio_perc AS nivel_atual
        FROM {tb('dim_pontos_rede')} p
        LEFT JOIN {tb('dim_setores')} s ON s.setor_id = p.setor_id
        LEFT JOIN (
            SELECT ponto_rede_id, pressao_mpa, vazao_l_min, nivel_reservatorio_perc
            FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY ponto_rede_id ORDER BY timestamp DESC) AS rn
                FROM {tb('fato_leituras_iot')}
            ) t WHERE rn = 1
        ) l ON l.ponto_rede_id = p.ponto_rede_id
        ORDER BY p.ponto_rede_id
    """)

    for p in pontos:
        for campo in ('latitude', 'longitude', 'pressao_atual', 'vazao_atual', 'nivel_atual'):
            if p.get(campo) is not None:
                p[campo] = float(p[campo])
        # Normalizar status para o frontend
        status = (p.get('status_operacional') or '').lower()
        if status in ('active', 'normal', 'ativo'):
            p['status_visual'] = 'normal'
        elif status in ('maintenance', 'manutencao', 'alerta'):
            p['status_visual'] = 'alerta'
        else:
            p['status_visual'] = 'critico'

    return jsonify(pontos)

@app.route('/api/dados/<string:ponto_id>', methods=['GET'])
def dados_ponto(ponto_id):

    # Telemetria mais recente do Databricks
    telemetria_rows = dbr(f"""
        SELECT pressao_mpa, vazao_l_min, nivel_reservatorio_perc,
               status_leitura, timestamp
        FROM {tb('fato_leituras_iot')}
        WHERE ponto_rede_id = '{ponto_id}'
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    telemetria = None
    if telemetria_rows:
        t = telemetria_rows[0]
        telemetria = {
            'pressao_mpa':             float(t['pressao_mpa'])             if t['pressao_mpa']             is not None else None,
            'vazao_l_min':             float(t['vazao_l_min'])             if t['vazao_l_min']             is not None else None,
            'nivel_reservatorio_perc': float(t['nivel_reservatorio_perc']) if t['nivel_reservatorio_perc'] is not None else None,
            'status_leitura':          t['status_leitura'],
            'timestamp':               str(t['timestamp']),
        }

    # Historico de perdas
    historico_perdas = dbr(f"""
        SELECT
            CAST(timestamp_analise AS DATE) AS data,
            ROUND(percentual_perda, 2)      AS percentual_perda,
            status_perda,
            tipo_perda,
            severidade,
            causa_provavel
        FROM {tb('fato_analise_perdas')}
        WHERE ponto_rede_id = '{ponto_id}'
        ORDER BY timestamp_analise DESC
        LIMIT 30
    """)

    for h in historico_perdas:
        if h.get('data'):
            h['data'] = str(h['data'])
        if h.get('percentual_perda') is not None:
            h['percentual_perda'] = float(h['percentual_perda'])

    # Eficiencia diaria do setor
    eficiencia = dbr(f"""
        SELECT
            CAST(c.data AS DATE)             AS data,
            ROUND(c.eficiencia_percentual,2) AS eficiencia_percentual,
            ROUND(c.consumo_total_l, 2)      AS consumo_total_l,
            ROUND(c.perda_estimada_l, 2)     AS perda_estimada_l,
            c.quantidade_alertas
        FROM {tb('fato_consumo_diario')} c
        WHERE c.setor_id = (
            SELECT setor_id FROM {tb('dim_pontos_rede')}
            WHERE ponto_rede_id = '{ponto_id}'
            LIMIT 1
        )
        ORDER BY c.data DESC
        LIMIT 7
    """)

    for e in eficiencia:
        if e.get('data'):
            e['data'] = str(e['data'])
        for campo in ('eficiencia_percentual', 'consumo_total_l', 'perda_estimada_l'):
            if e.get(campo) is not None:
                e[campo] = float(e[campo])

    # Alertas abertos
    alertas = dbr(f"""
        SELECT
            tipo_alerta,
            severidade,
            descricao,
            status_alerta,
            prioridade_operacional,
            equipe_responsavel,
            CAST(timestamp_alerta AS STRING) AS timestamp_alerta
        FROM {tb('fato_alertas')}
        WHERE ponto_rede_id = '{ponto_id}'
          AND status_alerta = 'Open'
        ORDER BY timestamp_alerta DESC
        LIMIT 5
    """)

    # Manutencoes recentes
    manutencoes = dbr(f"""
        SELECT
            tipo_manutencao,
            descricao_manutencao,
            status_manutencao,
            equipe_tecnica,
            impacto,
            clientes_afetados,
            CAST(data_hora_inicio AS STRING) AS data_hora_inicio,
            CAST(data_hora_fim    AS STRING) AS data_hora_fim
        FROM {tb('fato_manutencoes')}
        WHERE ponto_rede_id = '{ponto_id}'
        ORDER BY data_hora_inicio DESC
        LIMIT 3
    """)

    return jsonify({
        'ponto_id':         ponto_id,
        'telemetria':       telemetria,
        'historico_perdas': historico_perdas,
        'eficiencia':       eficiencia,
        'alertas':          alertas,
        'manutencoes':      manutencoes,
    })

@app.route('/api/alertas', methods=['GET'])
def get_alertas():
    ponto_id = request.args.get('ponto_id')
    filtro   = f"AND a.ponto_rede_id = '{ponto_id}'" if ponto_id else ""
    alertas = dbr(f"""
        SELECT
            a.tipo_alerta, a.severidade, a.descricao,
            a.status_alerta, a.prioridade_operacional,
            a.equipe_responsavel, p.nome_ponto,
            CAST(a.timestamp_alerta AS STRING) AS timestamp_alerta
        FROM {tb('fato_alertas')} a
        JOIN {tb('dim_pontos_rede')} p ON p.ponto_rede_id = a.ponto_rede_id
        WHERE a.status_alerta = 'Open'
        {filtro}
        ORDER BY timestamp_alerta DESC
        LIMIT 50
    """)
    return jsonify(alertas if alertas else [])

# SQL Server continua recebendo dados do hardware IoT
@app.route('/api/sensor/leitura', methods=['POST'])
def receber_leitura():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Nenhum dado enviado'}), 400
    sensor_id = dados.get('id_sensor')
    vazao     = dados.get('valor')
    pressao   = dados.get('pressao', 0.32)
    info = executar_query(
        "SELECT ponto_rede_id, setor_id FROM dim_sensores WHERE sensor_id = ?",
        (sensor_id,)
    )
    if not info:
        return jsonify({'erro': f"Sensor nao cadastrado"}), 404
    leitura_id = 'L-' + str(uuid.uuid4())[:8].upper()
    executar_query("""
        INSERT INTO fato_leituras_iot
            (leitura_id, sensor_id, ponto_rede_id, setor_id,
             timestamp, pressao_mpa, vazao_l_min, status_leitura)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Normal')
    """, (leitura_id, sensor_id, info[0]['ponto_rede_id'],
          info[0]['setor_id'], datetime.now(), pressao, vazao),
    retorno_dados=False)
    return jsonify({'status': 'sucesso', 'leitura_id': leitura_id}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
