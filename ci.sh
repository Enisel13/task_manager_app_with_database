#!/bin/bash

echo "Building Docker image for task-manager-app:v1"
docker build -t task-manager-app:"$1" ./app
echo "Building image done"
docker image ls