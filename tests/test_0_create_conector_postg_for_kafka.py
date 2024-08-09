import pytest
import requests
import json
import logging

# Configurar o logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Defina o URL do endpoint do Debezium
debezium_url = "http://localhost:8083/connectors"

# Função para verificar o endpoint do Debezium
def check_debezium():
    try:
        response = requests.get(debezium_url)
        response.raise_for_status()  # Lança uma exceção para status de erro
        logger.debug(f"Response from Debezium: Status Code: {response.status_code}, Content: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao acessar o endpoint do Debezium: {e}")
        return None

# Função para enviar uma solicitação POST para criar um novo conector
def create_connector(json_file_path):
    try:
        # Leia o conteúdo do arquivo JSON
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
        
        # Envie a solicitação POST
        headers = {'Content-Type': 'application/json'}
        response = requests.post(debezium_url, headers=headers, json=json_data)
        
        # Log e retorno de status
        if response.status_code == 409:
            logger.info("Conector já existe.")
        elif response.status_code == 201:
            logger.info("Conector criado com sucesso.")
        else:
            logger.debug(f"Status code: {response.status_code}")
        
        # Retorna a resposta
        return response
    
    except requests.exceptions.RequestException as e:
        # Loga a exceção e retorna uma resposta com status 500 e o erro como conteúdo
        logger.error(f"Erro ao criar o conector: {e}")
        return requests.Response()._replace(status_code=500, text=str(e))

@pytest.fixture
def mock_json_file(tmpdir):
    json_data = {
        "name": "source-condomanager-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": "postgres",
            "database.port": "5432",
            "database.user": "myuser",
            "database.password": "mypassword",
            "database.dbname": "mydatabase",
            "plugin.name": "pgoutput",
            "database.server.name": "source",
            "key.converter.schemas.enable": "false",
            "value.converter.schemas.enable": "false",
            "transforms": "unwrap",
            "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "key.converter": "org.apache.kafka.connect.json.JsonConverter",
            "table.include.list": "public.condominios, public.moradores, public.imoveis, public.transacoes",
            "slot.name": "dbz_condominios_transaction_slot"
        }
    }
    json_file = tmpdir.join("register-postgres.json")
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=4)
    return str(json_file)

def test_check_debezium():
    response = check_debezium()
    if response:
        logger.debug(f"Test check_debezium response: Status Code: {response.status_code}, Content: {response.text}")
        
        # Verifica se a resposta está vazia
        if not response.json():
            logger.info("A resposta do endpoint Debezium está vazia.")
        else:
            logger.info(f"Conectores encontrados: {response.json()}")
        
        # Valida o status code
        assert response.status_code in [200, 409]  # Verifica se o status é 200 ou 409
        
    else:
        logger.error("Falha ao obter a resposta do endpoint Debezium.")
        assert False  # Garante que o teste falhará se a resposta for None

def test_create_connector(mock_json_file):
    response = create_connector(mock_json_file)
    logger.debug(f"RESPONSE RETORNADO FOI ###########: {response.status_code}, response: {response}")

    logger.debug(f"Test create_connector response: Status Code: {response.status_code}, Content: {response.text}")

    # Verifica se o status é 201 ou 409
    assert response.status_code in [201, 409]
