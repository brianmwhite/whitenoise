#!/usr/bin/bash

SERVICENAME="whitenoise"
DELETEPICKLE=false
DATESTAMP=$(date +%Y-%m-%d)

git fetch

if [ "$(git rev-parse HEAD)" != "$(git rev-parse @\{u\})" ]; then

    while true; do
        read -rp "Delete saved[pickle] data? [yN] " yn
        case $yn in
            [Yy]* ) DELETEPICKLE=true; break;;
            [Nn]* ) DELETEPICKLE=false; break;;
            * ) DELETEPICKLE=false; break;;
        esac
    done

    echo "updating code from repo"
    git pull

    # previously...
    # git fetch --all
    # git reset --hard origin/master

    echo "building docker image"
    docker build . --tag $SERVICENAME --tag $SERVICENAME:v$DATESTAMP

    echo "stopping $SERVICENAME"
    docker-compose down

    if [ "$DELETEPICKLE" = true ] ; then
        echo "deleting $SERVICENAME.pickle file"
        rm config/$SERVICENAME.pickle
    fi

    echo "starting $SERVICENAME in background"
    docker-compose up -d

    echo "show $SERVICENAME logs"
    docker logs -f --since 1m $SERVICENAME
else
    echo "$SERVICENAME already up-to-date"
fi

