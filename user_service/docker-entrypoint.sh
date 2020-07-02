#!/bin/bash

set -e

until PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h "db" -p "5432" -q; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 3
done

>&2 echo "Postgres is up - executing command"

echo "The environment is: $ENVIRONMENT"

# Apply database migrations
flask db upgrade

# Start server
echo "Starting server"
python -m flask run --host=0.0.0.0
