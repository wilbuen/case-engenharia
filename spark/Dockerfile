FROM bitnami/spark:3.1.2

USER root

RUN curl -L -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.1.2.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.1.2/spark-sql-kafka-0-10_2.12-3.1.2.jar \
    && curl -L -o /opt/bitnami/spark/jars/kafka-clients-2.8.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.0/kafka-clients-2.8.0.jar

USER 1001
