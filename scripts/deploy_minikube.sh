#!/bin/bash
set -e

echo "Starting minikube with 4 CPUs, 8GB RAM"
minikube start --cpus=4 --memory=8192 --driver=docker

echo "Enable ingress addon"
minikube addons enable ingress

echo "Point docker env to minikube"
eval $(minikube docker-env)

echo "Build bot Docker image"
docker build -t telegram-bot:latest -f bot/Dockerfile .

echo "Deploy all resources via kustomize"
kubectl apply -k k8s/

echo "Wait for PostgreSQL to be ready"
kubectl wait --for=condition=ready pod -l app=postgres -n telegram-bot --timeout=120s

echo "Wait for Redis"
kubectl wait --for=condition=ready pod -l app=redis -n telegram-bot --timeout=60s

echo "Run database migrations (inside bot pod)"
BOT_POD=$(kubectl get pod -l app=telegram-bot -n telegram-bot -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $BOT_POD -n telegram-bot -- python -c "from bot.services.db import init_db; import asyncio; asyncio.run(init_db())"

echo "Get minikube IP"
MINIKUBE_IP=$(minikube ip)
echo "Add /etc/hosts entry: $MINIKUBE_IP bot.example.com (run with sudo if needed)"
echo "Ingress is configured. Bot webhook URL: https://bot.example.com/webhook"
echo "Deployment complete."