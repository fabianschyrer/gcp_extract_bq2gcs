#!/usr/bin/env bash

echo "################### Push to <DOCKER_REGISTRY> ###################".
gcloud docker -- push <DOCKER_REGISTRY>:latest