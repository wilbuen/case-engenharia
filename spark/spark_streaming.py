from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder \
    .appName("PostgresToLocal") \
    .getOrCreate()

kafka_brokers = "kafka:9092"
topics = ["dbserver1.public.condominios", "dbserver1.public.moradores", "dbserver1.public.imoveis", "dbserver1.public.transacoes"]

schema = StructType([
    StructField("before", StructType([
        StructField("condominio_id", StringType()),
        StructField("nome", StringType()),
        StructField("endereco", StringType())
    ])),
    StructField("after", StructType([
        StructField("condominio_id", StringType()),
        StructField("nome", StringType()),
        StructField("endereco", StringType())
    ])),
    StructField("source", StructType([
        StructField("version", StringType()),
        StructField("connector", StringType()),
        StructField("name", StringType()),
        StructField("ts_ms", StringType()),
        StructField("snapshot", StringType()),
        StructField("db", StringType()),
        StructField("schema", StringType()),
        StructField("table", StringType()),
        StructField("txId", StringType()),
        StructField("lsn", StringType()),
        StructField("xmin", StringType())
    ])),
    StructField("op", StringType()),
    StructField("ts_ms", StringType()),
    StructField("transaction", StructType([
        StructField("id", StringType()),
        StructField("total_order", StringType()),
        StructField("data_collection_order", StringType())
    ]))
])

def process_topic(topic):
    df = spark \
      .readStream \
      .format("kafka") \
      .option("kafka.bootstrap.servers", kafka_brokers) \
      .option("subscribe", topic) \
      .load()

    df = df.selectExpr("CAST(value AS STRING)")

    df = df.withColumn("data", from_json(col("value"), schema)) \
           .select("data.after.*")

    query = df.writeStream \
        .format("csv") \
        .option("path", f"/opt/spark/datalake/{topic.split('.')[-1]}") \
        .option("checkpointLocation", f"/opt/spark/datalake/checkpoints/{topic.split('.')[-1]}") \
        .start()

    return query

queries = [process_topic(topic) for topic in topics]

for query in queries:
    query.awaitTermination()
