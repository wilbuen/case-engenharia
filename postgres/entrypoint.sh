set -e

chown -R postgres:postgres "$PGDATA"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "Initializing database..."
  gosu postgres initdb

  if [ -f /etc/postgresql/postgresql.conf ]; then
    cp /etc/postgresql/postgresql.conf "$PGDATA/postgresql.conf"
  fi

  if [ -f /etc/postgresql/pg_hba.conf ]; then
    cp /etc/postgresql/pg_hba.conf "$PGDATA/pg_hba.conf"
  fi

  chown postgres:postgres "$PGDATA/postgresql.conf"
  chown postgres:postgres "$PGDATA/pg_hba.conf"
else
  echo "Data directory already exists, skipping initialization."
fi

exec gosu postgres postgres
