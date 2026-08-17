# Deployment

v1 hosts:

| Piece | Where |
|---|---|
| React UI | Vercel |
| FastAPI + joblib models | Railway |
| Logs / metrics tables | Supabase Postgres |

Live deploys need **your** accounts. Local Docker works without them.

## 1. Supabase

1. Create a project.
2. Run `docs/supabase.sql` in the SQL editor.
3. Copy **Project URL** and **service_role** key (not the anon key).

## 2. Railway (API)

1. New project → deploy from this GitHub repo (or `railway up` from the repo root).
2. Root directory: repository root (Dockerfile is at `/Dockerfile`).
3. Variables:

```
CORS_ORIGINS=https://YOUR-APP.vercel.app
MODELS_DIR=data/artifacts
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

4. Include `data/artifacts/*.joblib` in the image or upload them as a volume. Train locally first:

```bash
python -m src.models.train --task all
```

5. Confirm `https://YOUR-SERVICE.up.railway.app/health` and `/docs`.

If artifacts are gitignored, either commit them for the demo or add a Railway volume and copy the joblib files there.

## 3. Vercel (frontend)

1. Import `src/frontend` as the root directory (or set Root Directory to `src/frontend`).
2. Framework: Vite.
3. Environment variable:

```
VITE_API_BASE_URL=https://YOUR-SERVICE.up.railway.app
```

4. `vercel.json` already rewrites SPA routes to `index.html`.

## Local Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

API: http://localhost:8000/docs
