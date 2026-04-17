from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Permite que o app mobile e o site acessem essa API sem erros de segurança
CORS(app)

# Banco de dados simulado (enquanto os outros não criam o MySQL)
dados_vazamento = [
    {"id": 1, "local": "Torre A", "vazao": "45L/min", "status": "Crítico"},
    {"id": 2, "local": "Setor C", "vazao": "12L/min", "status": "Alerta"}
]

@app.route('/')
def home():
    return jsonify({"projeto": "SmartWater API", "status": "online", "versao": "1.0.0"})

# Rota que o Front-end vai usar para listar os alertas
@app.route('/api/alertas', methods=['GET'])
def get_alertas():
    return jsonify(dados_vazamento)

# Rota que o Hardware (Grupo 3) vai usar para enviar dados
@app.route('/api/sensor/leitura', methods=['POST'])
def receber_leitura():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado"}), 400
    
    # Aqui entraria a lógica de salvar no MySQL
    print(f"Recebido leitura do sensor {dados.get('id_sensor')}: {dados.get('valor')}L")
    
    return jsonify({"status": "sucesso", "mensagem": "Leitura registrada"}), 201

if __name__ == '__main__':
    # Roda em modo debug para facilitar o desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)