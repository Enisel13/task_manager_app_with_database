#!/bin/bash

if [[ -z "$1" ]]; then
  echo "Please provide a version tag as an argument."
  exit 1
fi
echo "Building Docker image for task-manager-app:$1"
# docker build --build-arg APP_VERSION="$1" -t task-manager-app:"$1" ./app
docker build --build-arg APP_VERSION="$1" -t containerregistrytaskmanager.azurecr.io/task-manager-app:"$1" ./app
docker push containerregistrytaskmanager.azurecr.io/task-manager-app:"$1"
echo "Building image done"
docker image ls
