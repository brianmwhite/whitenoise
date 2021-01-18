#!/bin/zsh

DATESTAMP=$(date +%Y-%m-%d)
git fetch --all
git reset --hard origin/master
docker build . --tag whitenoise --tag whitenoise:v$DATESTAMP
docker-compose down
docker-compose up -d