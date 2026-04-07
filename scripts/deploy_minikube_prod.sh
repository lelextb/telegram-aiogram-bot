#!/bin/bash
set -e

echo "Starting minikube"
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress

eval $(minikube docker-env)

echo "Building bot image"
docker build -t telegram-bot:latest -f bot/Dockerfile .

echo "Deploying with kustomize (including sealed secret)"
kubectl apply -k k8s/

echo "Waiting for PostgreSQL"
kubectl wait --for=condition=ready pod -l app=postgres -n telegram-bot --timeout=120s

echo "Waiting for Redis"
kubectl wait --for=condition=ready pod -l app=redis -n telegram-bot --timeout=60s

echo "Running database migrations"
BOT_POD=$(kubectl get pod -l app=telegram-bot -n telegram-bot -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $BOT_POD -n telegram-bot -- python -c "from bot.services.db import init_db; import asyncio; asyncio.run(init_db())"

echo "Deployment complete"
MINIKUBE_IP=$(minikube ip)
echo "Add to /etc/hosts: $MINIKUBE_IP bot.example.com"
echo "Set Telegram webhook to: https://bot.example.com/webhook"