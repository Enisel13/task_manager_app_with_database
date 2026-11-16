#!/bin/bash

echo "Deployment started"
# if [[ -z "$1" ]]; then
#   echo "Please provide a version tag as an argument."
#   exit 1
# fi

if [[ $# -ne 1 || ! "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "Usage: bash cd.sh <image-tag>"
  exit 1
fi

command -v kubectl >/dev/null 2>&1 || {
  echo "kubectl is not installed."
  exit 1
}

#kubectl set image deployment/task-manager-deployment task-manager-container=task-manager-app:"$1"

# Use k8s-aks for Azure or k8s-local for a local cluster; update both paths below.
sed -i '' "s|image: containerregistrytaskmanager.azurecr.io/task-manager-app:.*|image: containerregistrytaskmanager.azurecr.io/task-manager-app:${1}|" k8s-aks/deployment-app.yml
kubectl apply -f k8s-aks/
#kubectl rollout status deployment/task-manager-deployment


echo "Deployment done"