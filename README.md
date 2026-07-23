# 📚 Book Summary Platform

A full-stack app for creating, browsing, searching, and publishing **book
summaries**, with automatic cross-posting to Medium. Django REST Framework +
PostgreSQL full-text search on the backend, React (Vite) on the frontend.

![Book Summary Platform — home grid with search and tag filters](docs/screenshot.jpg)

- **Backend** — Django + DRF, token auth, PostgreSQL full-text search
  (`SearchVectorField` + GIN index), a pluggable Medium cross-post service, and a
  pytest suite at **100% coverage**.
- **Frontend** — Vite + React, Context + custom hooks (no Redux), a live
  debounced search, tag-filter chips, a Markdown editor (`@uiw/react-md-editor`),
  and Markdown rendering (`react-markdown`).
- **Ops** — one `docker compose up` brings up Django + React (nginx) + Postgres.

> **Medium note:** Medium's public posting API / integration tokens are largely
> discontinued, so real cross-posting won't work for most people. The service is
> **pluggable with a mock default** (`MEDIUM_MOCK=1`): publishing returns a
> plausible fake Medium URL so the feature is demoable end-to-end without a token.
> Set a real per-user token and `MEDIUM_MOCK=0` to attempt the real API. Either
> way, if Medium fails the summary is still published locally and the error logged.

---

## Run with Docker Compose

**Prerequisites:** Docker + Docker Compose.

```bash
cd book-summary-platform
docker compose up --build
```

This starts three services and **seeds sample data** on first boot
(`SEED_ON_START=1`). Then open:

| Service      | URL                              |
| ------------ | -------------------------------- |
| Frontend     | http://localhost:8080            |
| Backend API  | http://localhost:8000/api        |
| Django admin | http://localhost:8000/admin      |
| Postgres     | localhost:5432 (postgres/postgres) |

Seeded logins: **alice** / `password123`, **bob** / `password123`.

Stop and wipe the database volume:

```bash
docker compose down -v
```

### Local dev (without Docker)

```bash
# Backend (needs a running PostgreSQL)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit DATABASE_URL to point at your Postgres
python manage.py migrate
python manage.py seed
python manage.py runserver     # http://localhost:8000

# Frontend
cd ../frontend
npm install
cp .env.example .env           # VITE_API_URL=http://localhost:8000/api
npm run dev                    # http://localhost:5173
```

---

## Running the tests

The suite runs against **PostgreSQL** (required — full-text search cannot run on
SQLite). `pytest.ini` enforces `--cov-fail-under=90`.

```bash
cd backend
# point DATABASE_URL at a Postgres the test user can create databases on:
DATABASE_URL=postgres://postgres:postgres@localhost:5432/booksummaries \
SECRET_KEY=test-secret \
pytest
```

Or spin up a throwaway Postgres for tests:

```bash
docker run -d --name bsp-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=booksummaries -p 5432:5432 postgres:16-alpine
DATABASE_URL=postgres://postgres:postgres@localhost:5432/booksummaries \
SECRET_KEY=test-secret pytest
```

Coverage covers auth, CRUD, full-text search, tag filtering, the publish endpoint
(Medium mocked), profiles, and the seed command. CI (`.github/workflows/ci.yml`)
runs the suite against a Postgres service on every push.

---

## Setting up Medium integration

1. **Get a token (historical).** Medium integration tokens were issued at
   *Medium → Settings → Security and apps → Integration tokens*. Medium has since
   wound this down, so new tokens generally can't be created — hence the mock
   default below.
2. **Store it on your profile.** In the app, open **My Profile → Profile settings
   → Medium integration token** and save it. (API: `PATCH /api/profile/me` with
   `{"medium_token": "..."}`.) The token is write-only and never returned by the API.
3. **Turn off mock mode** to attempt real posting: set the backend env var
   `MEDIUM_MOCK=0` (in `docker-compose.yml` or `.env`). With a token present and
   mock off, **Publish to Medium** calls
   `POST https://api.medium.com/v1/users/:userId/posts`.

| Env var           | Default                     | Purpose |
| ----------------- | --------------------------- | ------- |
| `MEDIUM_MOCK`     | `1`                         | Return a fake Medium URL without calling the API (demo). |
| `MEDIUM_API_BASE` | `https://api.medium.com/v1` | Medium API base URL. |

The per-user token lives on `UserProfile.medium_token`, never in an env var.

---

## API reference

Base URL `http://localhost:8000`. Authenticated requests send
`Authorization: Token <token>`.

### Auth
| Method | Path                 | Auth | Body / notes |
| ------ | -------------------- | ---- | ------------ |
| POST   | `/api/auth/register` | –    | `{username, email?, password}` → `{token, user}` |
| POST   | `/api/auth/login`    | –    | `{username, password}` → `{token, user}` |
| POST   | `/api/auth/logout`   | ✔    | invalidates the token → 204 |

### Summaries
| Method | Path                          | Auth | Notes |
| ------ | ----------------------------- | ---- | ----- |
| GET    | `/api/summaries`              | –    | paginated; `?search=` (full-text), `?tag=<slug>`, `?page=`, `?mine=true` (own, incl. drafts) |
| POST   | `/api/summaries`              | ✔    | `{title, author, body, tags: [names]}` → created (draft) |
| GET    | `/api/summaries/:id`          | –    | detail (owner may view own drafts) |
| PUT/PATCH | `/api/summaries/:id`       | owner | update |
| DELETE | `/api/summaries/:id`          | owner | 204 |
| POST   | `/api/summaries/:id/publish`  | owner | sets `is_published=True`, cross-posts to Medium |

### Tags & profiles
| Method | Path                          | Auth | Notes |
| ------ | ----------------------------- | ---- | ----- |
| GET    | `/api/tags`                   | –    | `[{id, name, slug, summary_count}]` (published counts) |
| GET    | `/api/users/:id/profile`      | –    | public profile + that user's published summaries |
| GET    | `/api/profile/me`             | ✔    | own profile (`has_medium_token`, bio, avatar) |
| PUT/PATCH | `/api/profile/me`          | ✔    | update bio / avatar_url / medium_token |
| GET    | `/health/`                    | –    | liveness |

---

## Design notes

- **PostgreSQL everywhere.** Search uses `SearchVector`/`SearchQuery`/`SearchRank`
  against a GIN-indexed `SearchVectorField` (title weighted above body). This is
  Postgres-only, so dev, tests, and prod all use Postgres.
- **User model.** Uses Django's built-in `User` plus a `UserProfile` one-to-one
  (bio, avatar_url, Medium token), auto-created via a `post_save` signal.
- **Medium service** (`summaries/services/medium.py`) is isolated and never raises
  into the request path — a failed cross-post is logged and publishing still
  succeeds locally.
- **Secrets via env vars** (`SECRET_KEY`, `DATABASE_URL`, `MEDIUM_*`, CORS origins).
