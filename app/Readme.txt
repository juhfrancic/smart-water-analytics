# 💧 Smart Water — Sistema de Monitoramento de Saneamento

Sistema de monitoramento em tempo real da rede de saneamento de Araraquara, desenvolvido como projeto acadêmico integrado. Combina sensores IoT, banco de dados local (SQL Server), pipeline de dados em nuvem (Databricks) e um dashboard SCADA interativo no navegador.

---

## 🗺️ O que o sistema faz

- Exibe no mapa todos os pontos de monitoramento da rede hídrica de Araraquara
- Agrupa pontos próximos por bairro (Monitoring Node, Pressure Point, Flow Meter, Backup)
- Ao clicar em um bairro, abre um dashboard com:
  - **Pressão média** (MPa)
  - **Vazão média** (L/min)
  - **Nível do reservatório** (%)
  - **Timestamp da última leitura**
  - **Gráfico de tendência de perdas** — últimos 30 dias
  - **Gráfico de eficiência do setor** — últimos 7 dias
  - **Alertas ativos** com severidade e equipe responsável
  - **Manutenções recentes** com status e clientes afetados
- Recebe leituras de sensores IoT via API REST e salva no SQL Server local
- Busca dados analíticos históricos direto do Databricks (camada Gold)

---

## 🏗️ Arquitetura

```
Sensores IoT (Hardware)
        │
        ▼
  Flask API (backend)
   ├── SQL Server local   ← recebe leituras IoT em tempo real
   └── Databricks Gold    ← busca dados analíticos e históricos
        │
        ▼
  Dashboard (frontend)
  Leaflet.js + Chart.js
```

---

## 📁 Estrutura do projeto

```
smart-water/
└── app/
    ├── backend/
    │   ├── app.py              # API Flask principal
    │   ├── requirements.txt    # Dependências Python
    │   ├── .env                # Variáveis de ambiente (NÃO sobe no Git)
    │   └── .env.example        # Modelo de variáveis de ambiente
    └── frontend/
        ├── templates/
        │   └── index.html      # Interface principal
        └── static/
            ├── css/
            │   └── style.css   # Estilos do dashboard SCADA
            └── js/
                └── main.js     # Lógica do mapa e dashboard
```

---

## ⚙️ Pré-requisitos

- Python 3.14+
- SQL Server local com banco `saneamento_db`
- ODBC Driver 17 for SQL Server instalado
- Conta no Databricks com warehouse SQL ativo
- Tabelas no schema `workspace.gold`:
  - `dim_pontos_rede`
  - `dim_setores`
  - `dim_sensores`
  - `fato_leituras_iot`
  - `fato_analise_perdas`
  - `fato_consumo_diario`
  - `fato_alertas`
  - `fato_manutencoes`

---

## 🚀 Como rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/smart-water.git
cd smart-water/app/backend
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
DATABRICKS_HOST=seu-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/SEU_ID
DATABRICKS_TOKEN=seu_token_aqui
DATABRICKS_CATALOG=workspace
DATABRICKS_SCHEMA=gold
```

> ⚠️ O arquivo `.env` está no `.gitignore` e **nunca deve ser commitado**.

### 4. Rode o servidor

```powershell
# Windows PowerShell
& python app.py
```

```bash
# Linux / Mac
python app.py
```

### 5. Acesse no navegador

```
http://localhost:5000
```

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Interface principal (mapa + dashboard) |
| GET | `/api/pontos` | Lista todos os pontos de monitoramento |
| GET | `/api/dados/<ponto_id>` | Telemetria, histórico, alertas e manutenções de um ponto |
| GET | `/api/alertas` | Lista alertas abertos (todos ou por ponto) |
| POST | `/api/sensor/leitura` | Recebe leitura de sensor IoT |

### Exemplo de leitura IoT (POST)

```json
{
  "id_sensor": "SEN-001",
  "valor": 12.5,
  "pressao": 0.32
}
```

---

## 📊 Dados exibidos no dashboard

| Dado | Fonte | Tabela |
|------|-------|--------|
| Pontos no mapa | Databricks | `dim_pontos_rede` |
| Pressão, Vazão, Nível | Databricks | `fato_leituras_iot` |
| Tendência de perdas | Databricks | `fato_analise_perdas` |
| Eficiência do setor | Databricks | `fato_consumo_diario` |
| Alertas ativos | Databricks | `fato_alertas` |
| Manutenções recentes | Databricks | `fato_manutencoes` |
| Leituras IoT em tempo real | SQL Server local | `fato_leituras_iot` |

---

## 🛠️ Tecnologias utilizadas

**Backend**
- Python 3.14
- Flask 3.1
- pyodbc — conexão SQL Server
- databricks-sql-connector — conexão Databricks
- python-dotenv — variáveis de ambiente
- flask-cors — acesso externo (hardware IoT)

**Frontend**
- Leaflet.js — mapa interativo
- Chart.js — gráficos de linha e barra
- HTML5 + CSS3 (tema escuro SCADA)

**Dados**
- SQL Server — ingestão de dados IoT em tempo real
- Databricks (Delta Lake / camada Gold) — dados analíticos e históricos

---

## 👥 Equipe

Projeto acadêmico desenvolvido por múltiplos grupos integrados:
- **Grupo Frontend/Backend** — dashboard e API
- **Grupo Hardware** — sensores IoT e envio de leituras
- **Grupo Dados** — pipeline Databricks (Bronze → Silver → Gold)