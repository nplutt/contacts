#!/bin/bash

export DB_HOST="127.0.0.1"
export DB_PORT=0
export MASTER_DB_USER="master_local_docker_user"
export MASTER_DB_PASSWORD="master_local_docker_password"
export DB_USER="local_docker_user"
export DB_PASSWORD="local_docker_password"
export DB_NAME="postgres"

docker run -d -p 127.0.0.1:0:5432/tcp -e "POSTGRES_PASSWORD=${MASTER_DB_PASSWORD}" \
    -e "POSTGRES_USER=${MASTER_DB_USER}" postgres
container=$(docker ps --format "{{.Names}}" | head -n1 | sed -e 's/\s.*$//')
export DB_PORT=$(cut -d ":" -f 2 <<< $(docker port ${container} 5432))
echo "Waiting 10 seconds for docker image to start up..."
sleep 10
alembic upgrade head

chalice local