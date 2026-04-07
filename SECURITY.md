# Security Policy

## Supported Versions

Only the latest major version is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability within the bot, please follow these steps:

1. **Do NOT** disclose the issue publicly.
2. Send an email to **lelexthbest@gmail.com**
3. Include as much detail as possible: steps to reproduce, potential impact, and any suggested fix.
4. You can expect an initial response within 48 hours.

We will work with you to validate and fix the issue, and will credit you in the release notes if desired.

## Security Measures Implemented

The bot includes the following security features:

- **Rate limiting** – per‑user sliding window (5 commands per 10 seconds) prevents abuse.
- **Input validation** – all user inputs are sanitized before processing (Telethon/aiogram already handle basic sanitization).
- **Auto‑moderation** – configurable bad‑word filter and spam detection.
- **Database protection** – uses parameterized queries (SQLAlchemy) to prevent SQL injection.
- **Secret management** – for production, use SealedSecrets in Kubernetes to encrypt `BOT_TOKEN` and database passwords.
- **Webhook verification** – if webhook mode is used, requests are validated with a secret token.
- **Session isolation** – each user session is isolated; no cross‑user data leakage.

## Environment Variables

Never commit `.env` files. Use environment variables for all secrets:

- `BOT_TOKEN` – Telegram bot token (keep secret)
- `DATABASE_URL` – PostgreSQL connection string (contains password)
- `REDIS_URL` – Redis connection string

## Reporting Non‑Security Bugs

For non‑security issues, please use the GitHub issue tracker.

## Responsible Disclosure

We follow the principle of responsible disclosure. After a fix is released, we will publicly acknowledge the reporter (if they wish).

## Third‑Party Dependencies

Regularly update dependencies to patch known vulnerabilities. Run `pip list --outdated` and `safety check` (if installed) to monitor.
