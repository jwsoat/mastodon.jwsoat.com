# Mastodon.jwsoat.com — Docker Compose deployment

This repository builds a custom Mastodon image pinned to Mastodon `v4.5.2` with a **50,000-character status limit**.

The stack includes:

- Mastodon web
- Mastodon streaming API
- Sidekiq
- PostgreSQL 14
- Redis 7
- Caddy 2 with automatic HTTPS

## Requirements

- Linux VPS with Docker Engine and Docker Compose v2
- At least 4 GB RAM plus swap; 8 GB RAM is preferable
- A DNS `A`/`AAAA` record for `mastodon.jwsoat.com` pointing to the VPS
- TCP ports `80` and `443` available
- SMTP credentials for registration and password-reset email

## First-time setup

```bash
git clone https://github.com/jwsoat/mastodon.jwsoat.com.git
cd mastodon.jwsoat.com

cp .env.example .env
cp .env.production.example .env.production
chmod 600 .env .env.production
```

Edit both files. Use the same database password in `.env` as `DB_PASS` in `.env.production`.

Generate application secrets using the custom image after it has been built:

```bash
docker compose build web sidekiq

docker compose run --rm web bundle exec rails secret
docker compose run --rm web bundle exec rails mastodon:webpush:generate_vapid_key
```

Put the generated values into `.env.production` as `SECRET_KEY_BASE`, `VAPID_PRIVATE_KEY`, and `VAPID_PUBLIC_KEY`. Generate `OTP_SECRET` with another `rails secret` command.

Create the database and administrator account:

```bash
mkdir -p public/system

docker compose run --rm web bundle exec rails db:setup
# Optional interactive administrator creation:
docker compose run --rm web bundle exec rails mastodon:setup
```

Start the stack:

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
```

Caddy obtains the TLS certificate automatically once DNS resolves and ports 80/443 reach the VPS.

## Updating Mastodon

The image version is pinned in `.env`:

```bash
MASTODON_VERSION=4.5.2
```

To upgrade, change the version, then rebuild and restart:

```bash
docker compose build --pull web sidekiq
docker compose up -d
```

Review Mastodon's release notes before upgrading. Back up `postgres14/`, `redis/`, and `public/system/` first.

## Why the 50,000 limit works

The Dockerfile starts from the official Mastodon image and patches:

```ruby
MAX_CHARS = 500
```

to:

```ruby
MAX_CHARS = 50000
```

Mastodon 4.3+ exposes `StatusLengthValidator::MAX_CHARS` through the instance configuration API, so the web composer receives `50000` automatically. The backend validator is the authoritative limit.

## Important security notes

- Never commit `.env` or `.env.production`.
- Replace every `CHANGE_ME` value before exposing the server.
- Use a long random PostgreSQL password and strong Rails secrets.
- Keep the VPS operating system and Docker updated.
- Set up backups before accepting real user data.
