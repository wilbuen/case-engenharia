import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.access(directory, os.W_OK):
        raise PermissionError(f"Cannot write to directory {directory}")

base_data_path = "datalake/raw/"
base_checkpoint_path = "datalake/raw/checkpoints/"

ensure_dir(base_data_path)
ensure_dir(base_checkpoint_path)

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "4") \
    .config("spark.cores.max", "16") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.streaming.receiver.maxRate", "10000") \
    .config("spark.streaming.kafka.maxRatePerPartition", "1000") \
    .config("spark.streaming.kafka.consumer.cache.enabled", "false") \
    .config("spark.streaming.unpersist", "true") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1") \
    .getOrCreate()

schemas = {
    "source.public.condominios": StructType([
        StructField("condominio_id", IntegerType(), True),
        StructField("nome", StringType(), True),
        StructField("endereco", StringType(), True)
    ]),
    "source.public.moradores": StructType([
        StructField("morador_id", IntegerType(), True),
        StructField("nome", StringType(), True),
        StructField("condominio_id", IntegerType(), True),
        StructField("data_registro", StringType(), True)
    ]),
    "source.public.imoveis": StructType([
        StructField("imovel_id", IntegerType(), True),
        StructField("tipo", StringType(), True),
        StructField("condominio_id", IntegerType(), True),
        StructField("valor", StringType(), True)
    ]),
    "source.public.transacoes": StructType([
        StructField("transacao_id", IntegerType(), True),
        StructField("imovel_id", IntegerType(), True),
        StructField("morador_id", IntegerType(), True),
        StructField("data_transacao", StringType(), True),
        StructField("valor_transacao", StringType(), True)
    ])
}

topics = ",".join(schemas.keys())

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:29092") \
    .option("subscribe", topics) \
    .option("startingOffsets", "earliest") \
    .load()

queries = []

for topic, schema in schemas.items():
    topic_df = kafka_df.filter(col("topic") == topic)

    df = topic_df.selectExpr("CAST(value AS STRING) as json") \
                 .select(from_json(col("json"), schema).alias("data")) \
                 .select("data.*")

    topic_sanitized = topic.replace(".", "_")
    topic_data_path = os.path.join(base_data_path, topic_sanitized)
    topic_checkpoint_path = os.path.join(base_checkpoint_path, topic_sanitized)

    ensure_dir(topic_data_path)
    ensure_dir(topic_checkpoint_path)

    parquet_query = df.writeStream \
        .format("parquet") \
        .option("path", topic_data_path) \
        .option("checkpointLocation", topic_checkpoint_path) \
        .outputMode("append") \
        .start()

    queries.append(parquet_query)

    console_query = df.writeStream \
        .format("console") \
        .outputMode("append") \
        .start()

    queries.append(console_query)

for query in queries:
    query.awaitTermination()
