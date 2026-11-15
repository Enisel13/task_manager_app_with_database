#!/bin/bash

echo "Deployment started"

#kubectl set image deployment/task-manager-deployment task-manager-container=task-manager-app:"$1"
sed -i '' "s|image: task-manager-app:.*|image: task-manager-app:${1}|" k8s/deployment-app.yml
kubectl apply -f k8s/
#kubectl rollout status deployment/task-manager-deployment


echo "Deployment done"