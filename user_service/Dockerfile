FROM python:3.7

# create a migrations folder for migrations to be mounted as a volume
# in the user service (defined in docker-compose.yml)
RUN mkdir -p /user_service/migrations

WORKDIR /user_service/

COPY requirements.txt /user_service/

RUN pip install -r requirements.txt

COPY . /user_service/

EXPOSE 5000

ENV FLASK_APP=api

# pg_ready command is installed through this package.
# The command will be used to poll the "db" container to check if postgres is
# ready to accept connections. When ready, migrations will be run.
RUN apt-get update && apt-get install -f -y postgresql-client

RUN chown root:root /user_service/docker-entrypoint.sh && chmod 755 /user_service/docker-entrypoint.sh

ENTRYPOINT ./docker-entrypoint.sh
