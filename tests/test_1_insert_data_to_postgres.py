import random
from datetime import datetime, timedelta
import psycopg2
import pytest
import random
from datetime import datetime, timedelta

def generate_data(num_records):
    condominios_data = [
        f"('Condominio {i}', 'Endereço {i}')" for i in range(1, num_records + 1)
    ]

    moradores_data = [
        f"('Morador {i}', {i}, '{(datetime.now() - timedelta(days=i)).date()}')" for i in range(1, num_records + 1)
    ]

    imoveis_data = [
        f"('Apartamento', {i}, {random.uniform(100000, 500000):.2f})" for i in range(1, num_records + 1)
    ] + [
        f"('Casa', {i}, {random.uniform(100000, 500000):.2f})" for i in range(num_records + 1, 2 * num_records + 1)
    ]

    transacoes_data = [
        f"({random.randint(1, num_records)}, {random.randint(1, num_records)}, '{(datetime.now() - timedelta(days=i)).date()}', {random.uniform(100000, 500000):.2f})" for i in range(1, num_records + 1)
    ]

    v2_migration = f"""
    INSERT INTO condominios (nome, endereco) VALUES {', '.join(condominios_data)};
    INSERT INTO moradores (nome, condominio_id, data_registro) VALUES {', '.join(moradores_data)};
    INSERT INTO imoveis (tipo, condominio_id, valor) VALUES {', '.join(imoveis_data[:num_records])};
    INSERT INTO transacoes (imovel_id, morador_id, data_transacao, valor_transacao) VALUES {', '.join(transacoes_data)};
    """
    print(v2_migration)
    return v2_migration


def execute_migration(sql, conn_params):
    conn = psycopg2.connect(**conn_params)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()

def get_record_counts(conn_params):
    conn = psycopg2.connect(**conn_params)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM condominios")
            condominios_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM moradores")
            moradores_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM imoveis")
            imoveis_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM transacoes")
            transacoes_count = cursor.fetchone()[0]

        return condominios_count, moradores_count, imoveis_count, transacoes_count
    finally:
        conn.close()

@pytest.fixture
def db_connection_params():
    return {
        'dbname': 'mydatabase',
        'user': 'myuser',
        'password': 'mypassword',
        'host': 'localhost',
        'port': '5433'      
    }

def test_data_population(db_connection_params):
    num_records =1
    migration_sql = generate_data(num_records)
    
    initial_counts = get_record_counts(db_connection_params)
    
    execute_migration(migration_sql, db_connection_params)
    
    final_counts = get_record_counts(db_connection_params)

    assert final_counts[0] == initial_counts[0] + num_records, "Incorrect number of records in condominios"
    assert final_counts[1] == initial_counts[1] + num_records, "Incorrect number of records in moradores"
    assert final_counts[2] == initial_counts[2] + num_records, "Incorrect number of records in imoveis"
    assert final_counts[3] == initial_counts[3] + num_records, "Incorrect number of records in transacoes"
