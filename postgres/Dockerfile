FROM postgres:13
COPY config/postgresql.conf /etc/postgresql/postgresql.conf
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

COPY sql/init.sql /docker-entrypoint-initdb.d/
COPY sql/populate_table.sql /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/*.sql

COPY config/pg_hba.conf /etc/postgresql/
COPY config/postgresql.conf /etc/postgresql/

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
