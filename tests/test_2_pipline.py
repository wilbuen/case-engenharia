import pytest
import os

from commons.etl import ProcessLayer


@pytest.fixture(scope="module")
def spark_session():
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("TestProcessLayer").getOrCreate()
    yield spark
    spark.stop()

@pytest.fixture(scope="function")
def process_layer(spark_session):
    return ProcessLayer()

@pytest.fixture(scope="function")
def temp_dirs():
    raw_dir = "./datalake/raw/"
    transform_dir = "./datalake/transform/"
    refined_dir = "./datalake/refined/"

    yield raw_dir, transform_dir, refined_dir


def test_full_pipeline(process_layer, temp_dirs):
    raw_dir, transform_dir, refined_dir = temp_dirs

    process_layer.transform(
        tables=["source_public_transacoes", "source_public_condominios", "source_public_imoveis", "source_public_moradores"],
        source_path=raw_dir,
        target_path=transform_dir
    )

    assert os.path.exists(os.path.join(transform_dir, "source_public_moradores")), "Transform path for 'source_public_moradores' does not exist."
    assert os.path.exists(os.path.join(transform_dir, "source_public_transacoes")), "Transform path for 'source_public_transacoes' does not exist."
    assert os.path.exists(os.path.join(transform_dir, "source_public_imoveis")), "Transform path for 'source_public_imoveis' does not exist."
    assert os.path.exists(os.path.join(transform_dir, "source_public_condominios")), "Transform path for 'source_public_condominios' does not exist."

    process_layer.refined(
        source_path=transform_dir,
        refined_path=refined_dir
    )

    assert os.path.exists(os.path.join(refined_dir, "transacoes_por_condominio")), "Refined data path for 'transacoes_por_condominio' does not exist."
    assert os.path.exists(os.path.join(refined_dir, "valor_total_por_morador")), "Refined data path for 'valor_total_por_morador' does not exist."
    assert os.path.exists(os.path.join(refined_dir, "transacoes_diarias_por_tipo")), "Refined data path for 'transacoes_diarias_por_tipo' does not exist."
