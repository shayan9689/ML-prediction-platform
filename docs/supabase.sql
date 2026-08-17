-- Run in the Supabase SQL editor before pointing Railway at the project.
-- RLS: deny anon; only the service role used by FastAPI should write.

create table if not exists prediction_logs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  task text not null,
  model_used text,
  input jsonb not null,
  prediction jsonb not null,
  latency_ms integer,
  error text
);

create table if not exists model_metrics (
  task text primary key,
  best_model text not null,
  metrics jsonb not null,
  comparison jsonb,
  feature_importance jsonb,
  trained_at timestamptz not null default now()
);

alter table prediction_logs enable row level security;
alter table model_metrics enable row level security;
