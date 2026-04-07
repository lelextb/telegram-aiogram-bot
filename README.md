## Complete Documentation – Telegram Bot + Analytics Dashboard

### Project Overview

This is a **production‑ready, autonomous Telegram bot** and its **real‑time analytics dashboard**.  
The bot handles **≥100 concurrent updates**, includes rate limiting, reminders, trades, temporary invites, auto‑moderation, and continuous fuzzing.  
The dashboard provides live command heatmaps, charts, moderation rule editor, trade viewer, invite manager, user management, and WebSocket‑based real‑time events.

Both components share the **same PostgreSQL database** and communicate via **Redis pub/sub** for real‑time events.  
The bot can be deployed locally (long polling) or on **Kubernetes (minikube)** with **SealedSecrets** for encrypted credentials.  
The dashboard runs on **Laravel 12 + Vue 3 + Inertia + Reverb**.

---

## Repository Links

- **Bot**: [https://github.com/lelextb/telegram-aiogram-bot](https://github.com/lelextb/telegram-aiogram-bot)
- **Dashboard**: [https://github.com/lelextb/telegram-bot-analytics](https://github.com/lelextb/telegram-bot-analytics)

---

## 1. Bot Setup & Configuration

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- (Optional) Docker / minikube for Kubernetes deployment

### Local Installation (Long Polling)

```bash
git clone https://github.com/lelextb/telegram-aiogram-bot.git
cd telegram-aiogram-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```ini
BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/telegram_db
REDIS_URL=redis://localhost:6379/0
USE_WEBHOOK=false   # long polling mode
```

Create the database:
```bash
sudo -u postgres psql -c "CREATE USER dashboard WITH PASSWORD 'secret';"
sudo -u postgres psql -c "CREATE DATABASE telegram_db OWNER dashboard;"
```

Run migrations (automatically created on first start):
```bash
python -m bot.main   # will create tables
```

Run the bot:
```bash
python -m bot.main
```

### Kubernetes Deployment (Webhook Mode)

1. Set `USE_WEBHOOK=true` in `.env`.
2. Build Docker image and push to your registry (or use minikube’s Docker daemon).
3. Install SealedSecrets controller in your cluster.
4. Create sealed secret (see README).
5. Apply all manifests in `k8s/` using `kubectl apply -k k8s/`.
6. Set the webhook URL via `curl` or use `@BotFather` with your domain.

---

## 2. Dashboard Setup & Configuration

### Prerequisites
- PHP 8.2+ (8.5 supported)
- Composer
- Node.js 20+ & npm
- PostgreSQL 14+
- Redis 7+

### Local Installation

```bash
git clone https://github.com/lelextb/telegram-bot-analytics.git
cd telegram-bot-analytics
composer install
npm install --legacy-peer-deps
cp .env.example .env
```

Edit `.env`:
```ini
APP_URL=http://localhost
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=telegram_db
DB_USERNAME=dashboard
DB_PASSWORD=secret

BROADCAST_DRIVER=reverb
REVERB_APP_ID=123456
REVERB_APP_KEY=your-reverb-key
REVERB_APP_SECRET=your-reverb-secret
REVERB_HOST=localhost
REVERB_PORT=8080
REVERB_SCHEME=http

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_ADMIN_IDS=7916393260   # your Telegram user ID
```

Run migrations and seed admin:
```bash
php artisan key:generate
php artisan migrate --seed
```

Build frontend:
```bash
npm run build
```

Start the services (three terminals):

```bash
# Terminal 1
php artisan serve --host=0.0.0.0 --port=8000

# Terminal 2
php artisan reverb:start

# Terminal 3
php artisan redis:subscribe
```

Visit `http://localhost:8000` and log in with Telegram.

### Docker Compose (All Services)

```bash
docker-compose up -d
```

The dashboard will be available at `http://localhost:8000`.

---

## 3. Integration Between Bot and Dashboard

- **Database**: Both use the same PostgreSQL instance. The bot writes to `command_logs`, `trades`, `temp_invites`, `moderation_logs`; the dashboard reads these tables.
- **Real‑time events**: The bot publishes Redis messages on channel `bot_events`. The dashboard runs `php artisan redis:subscribe` to listen and broadcasts them via WebSocket (Reverb) to the Vue frontend.
- **Moderation rules**: The dashboard CRUD operations modify the `moderation_rules` table. The bot reads this table to enforce rules.
- **No extra APIs** – all communication is through the shared database and Redis.

---

## 4. Profiling & Fuzzing

### Bot Fuzzing (Hypothesis)

```bash
cd fuzzing
pytest test_fuzz.py --hypothesis-show-statistics
```

### Memory Profiling (Valgrind) – local only

```bash
valgrind --tool=massif python -m bot.main
ms_print massif.out.*
```

### CPU Profiling (py‑spy)

```bash
py-spy record -o profile.svg -- python -m bot.main
```

---

## 5. Common Troubleshooting

### Bot
- **`ModuleNotFoundError: No module named 'bot'`** – ensure you are in the correct directory and have `__init__.py` files.
- **Redis connection error** – verify Redis is running (`redis-cli ping`) and `REDIS_URL` is correct.
- **Database column missing** – run migrations (`python -c "from bot.models.sqlalchemy_models import init_db; import asyncio; asyncio.run(init_db())"`).
- **Webhook not working** – check your domain is set with `@BotFather` and the webhook URL is public.

### Dashboard
- **`Driver [telegram] not supported`** – install `socialiteproviders/telegram` and add the event listener in `EventServiceProvider`.
- **Real‑time events not showing** – ensure `php artisan redis:subscribe` is running and Redis is reachable.
- **Mixed content / HTTPS** – set `APP_URL` to your HTTPS domain and force HTTPS in `AppServiceProvider`.
- **Telegram login “Page Expired”** – exclude `/auth/telegram/callback` from CSRF in `bootstrap/app.php`.

---

## 6. Security Considerations

- **Never commit `.env` files** – use `.env.example` as a template.
- **Use SealedSecrets** in Kubernetes to encrypt `BOT_TOKEN` and database passwords.
- **Rate limiting** prevents command spam.
- **Auto‑moderation** filters bad words.
- **Webhook secret token** verifies incoming requests (if using webhook mode).
- **Regularly update dependencies** to patch vulnerabilities.

---

## 7. Contributing

Both repositories are open for contributions. Please:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a clear description.

---

## 8. License

MIT – free to use, modify, and distribute.  
No warranty, use at your own risk.

--

## 9. LelexTB's Word & Credits

This project was conceived, architected, and brought to life by **LelexTB**.  
It represents a complete, production‑ready ecosystem for a high‑performance Telegram bot and its real‑time analytics dashboard – built with attention to concurrency, security, observability, and developer experience.

**Credits & Thanks**

- **aiogram** and **Telethon** communities for the excellent async Telegram libraries.
- **Laravel, Vue, Inertia, Reverb** – the backbone of the modern dashboard.
- **PostgreSQL & Redis** – reliable data and messaging backbone.
- **Hypothesis & AFL** – for making fuzzing accessible.
- **Bitnami SealedSecrets** – for Kubernetes secret encryption.
- **All open‑source contributors** whose packages made this possible.

**Special thanks** to early testers, issue reporters, and anyone who takes the time to understand, use, or improve this project.

If you find this project useful, consider giving it a ⭐ on GitHub, sharing feedback, or contributing.  
For questions or collaborations, reach out via GitHub Issues or Discussions.

— **LelexTB**  
*Agentic Architect • Multi‑Stack Engineer • Systems Architect*
