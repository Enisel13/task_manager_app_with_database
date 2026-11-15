#!/bin/bash

echo "Deployment started"
if [[ -z "$1" ]]; then
  echo "Please provide a version tag as an argument."
  exit 1
fi

#kubectl set image deployment/task-manager-deployment task-manager-container=task-manager-app:"$1"
sed -i '' "s|image: containerregistrytaskmanager.azurecr.io/task-manager-app:.*|image: containerregistrytaskmanager.azurecr.io/task-manager-app:${1}|" k8s/deployment-app.yml
kubectl apply -f k8s/
#kubectl rollout status deployment/task-manager-deployment


echo "Deployment done"