# 🤖 Telegram Autonomous Bot – High Concurrency, Reminders, Fuzzing, Kubernetes

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.13-blue)](https://docs.aiogram.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Asyncpg-blue)](https://www.postgresql.org)
[![Kubernetes](https://img.shields.io/badge/K8s-minikube-blue)](https://minikube.sigs.k8s.io)

**Autonomous Telegram bot** built with **aiogram** (Python).  
Handles **≥100 concurrent updates**, per‑user rate limiting, scheduled reminders (DM), command logging, trade system, temporary invites, auto‑moderation, and **continuous fuzzing** (Hypothesis + AFL).  
Deployable on **Kubernetes (minikube)** with **SealedSecrets** for encrypted credentials.

## ✨ Features
- ⚡ High concurrency (async, webhook or long polling)
- ⏲️ Per‑user rate limiting (5 commands / 10 sec)
- ⏰ Reminder system (DM notifications)
- 🤝 Trade initiation and confirmation (buttons)
- 🔗 Temporary invite links (expire, single‑use)
- 🛡️ Auto‑moderation (bad word filter, spam detection)
- 🔥 Continuous fuzzing (Hypothesis + AFL)
- 📦 Docker + Kubernetes manifests (SealedSecrets ready)
- 📊 Real‑time Redis pub/sub → dashboard integration

## 🚀 Quick Start (Local, no Kubernetes)

```bash
git clone https://github.com/lelextb/telegram-autonomous-bot.git
cd telegram-autonomous-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill BOT_TOKEN, DATABASE_URL, REDIS_URL
python -m bot.main
```

## 🐳 Production on Kubernetes (minikube)

```bash
# Install SealedSecrets controller
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets --namespace kube-system

# Create sealed secret (replace with your own token)
kubectl create secret generic bot-secret --dry-run=client -o yaml --namespace telegram-bot \
  --from-literal=BOT_TOKEN=your_token \
  --from-literal=POSTGRES_PASSWORD=your_password \
  --from-literal=WEBHOOK_SECRET=random_secret | kubeseal -o yaml > k8s/bot/bot-sealedsecret.yaml

# Deploy
eval $(minikube docker-env)
docker build -t telegram-bot:latest -f bot/Dockerfile .
kubectl apply -k k8s/
```

## 🔗 Integration with Dashboard
This bot shares the same PostgreSQL database with the [Telegram Bot Dashboard](https://github.com/lelextb/telegram-bot-analytics-dashboard).  
All command logs, reminders, trades, and moderation rules are visible in real time.

## 📝 License
MIT Free to use & Edit as needed
Feel free to submit a issue, request features, PR as well.