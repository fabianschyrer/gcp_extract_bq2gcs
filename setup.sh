#!/usr/bin/env bash

echo "################### Building Docker ... ###################"
echo "################### 1. create base image for python 3.6 build"
docker build -t extract.bq.to.gcs .

if [ $? -eq 0 ]
    then
        echo "Docker build & Test successfully"
    else
        exit 1
fi

echo "################### Tag to dataplatform's gcr ... ###################"
docker tag extract.bq.to.gcs <DOCKER_REGISTRY>:latest