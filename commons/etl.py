import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DecimalType
from pyspark.sql.functions import count, sum, col, date_format, unbase64, hex, conv, expr

class ProcessLayer:
    def __init__(self):
        self.spark = SparkSession.builder.appName("ProcessLayer").getOrCreate()

        # Esquemas das tabelas
        self.schemas = {
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

    def transform(self, tables, source_path, target_path):
        if isinstance(tables, str):
            tables = [tables]

        today = datetime.now()
        date_path = os.path.join(str(today.year), str(today.month).zfill(2), str(today.day).zfill(2))

        for table in tables:
            source_table_path = os.path.join(source_path, table)

            if not os.path.exists(source_table_path):
                continue

            df = self.spark.read.parquet(source_table_path)

            for col_name in df.columns:
                if "data" in col_name:
                    df = df.withColumn(col_name, col(col_name).cast("int"))
                    df = df.withColumn(col_name, expr(f"date_add('1970-01-01', {col_name})"))

                if "valor" in col_name:
                    df = df.withColumn(f"{col_name}_bin", unbase64(col(col_name)))
                    df = df.withColumn(f"{col_name}_hex", hex(col(f"{col_name}_bin")))
                    df = df.withColumn(col_name, conv(col(f"{col_name}_hex"), 16, 10).cast(DecimalType(15, 2)))
                    df = df.drop(f"{col_name}_bin", f"{col_name}_hex")


            target_table_path = os.path.join(target_path, table, date_path)
            df.write.mode("overwrite").parquet(target_table_path)
            print(f"Dados da tabela '{table}' movidos para '{target_table_path}'")

    def refined(self, source_path, refined_path):
        try:
            imovel_df = self.spark.read.schema(self.schemas["source.public.imoveis"]).parquet(os.path.join(source_path, "source_public_imoveis"))
            transacao_df = self.spark.read.schema(self.schemas["source.public.transacoes"]).parquet(os.path.join(source_path, "source_public_transacoes"))
        except Exception as e:
            print(f"Erro ao ler os arquivos Parquet: {e}")
            return

        print("Arquivos Parquet lidos com sucesso.")

        try:
            transacoes_por_condominio_df = transacao_df.groupBy("imovel_id").agg(count("transacao_id").alias("total_transacoes"))
            transacoes_por_condominio_df = transacoes_por_condominio_df.join(imovel_df, "imovel_id") \
                .groupBy("condominio_id").agg(sum("total_transacoes").alias("total_transacoes_por_condominio"))
        except Exception as e:
            print(f"Erro ao calcular total de transações por condomínio: {e}")
            return

        try:
            valor_total_por_morador_df = transacao_df.groupBy("morador_id").agg(
                sum(col("valor_transacao").cast("decimal(15,2)")).alias("valor_total_transacoes")
            )
        except Exception as e:
            print(f"Erro ao calcular valor total das transações por morador: {e}")
            return

        try:
            transacoes_diarias_por_tipo_df = transacao_df.join(imovel_df, "imovel_id") \
                .groupBy(date_format("data_transacao", "yyyy-MM-dd").alias("data_transacao"), "tipo") \
                .agg(
                    sum(col("valor_transacao").cast("decimal(15,2)")).alias("valor_total_diario"),
                    count("transacao_id").alias("total_transacoes_diarias")
                )
        except Exception as e:
            print(f"Erro ao agregar transações diárias por tipo de imóvel: {e}")
            return

        try:
            transacoes_por_condominio_df.write.mode("overwrite").parquet(os.path.join(refined_path, "transacoes_por_condominio"))
            valor_total_por_morador_df.write.mode("overwrite").parquet(os.path.join(refined_path, "valor_total_por_morador"))
            transacoes_diarias_por_tipo_df.write.mode("overwrite").parquet(os.path.join(refined_path, "transacoes_diarias_por_tipo"))
            print(f"Dados refinados salvos em '{refined_path}'")
        except Exception as e:
            print(f"Erro ao salvar os dados refinados: {e}")

    def stop_spark(self):
        self.spark.stop()
