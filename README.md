# The Daily Absurd

**The World Is Serious. We Don't Have To Be.**

An autonomous international satirical news publication. Software agents monitor
real-world events; **Devin** is the editorial staff that writes and reviews the
satire; deterministic pipelines handle scoring, SEO, safety checks, social
assets, publishing and analytics.

Everything on the site is fictional satire, clearly labelled as such.

## Layout

| Path | What lives there |
|---|---|
| `web/` | Next.js 15 + TypeScript + Tailwind v4 publication site (Vercel) |
| `web/content/articles/` | Published articles — JSON committed by the publishing agent; git is the CMS |
| `agents/` | `absurd_ops` Python package: the autonomous newsroom (stdlib only) |
| `agents/queue/` | Editorial queue: briefs, drafts, reviews, social packs |
| `agents/state/` | SQLite ops DB (gitignored) |
| `ops/systemd/` | Persistent `--user` services + timers |
| `docs/` | Architecture, agents, operations, monetization, deployment |

## Quick start

```bash
cd web && npm install && npm run build && npm start   # site on :3210
cd agents && PYTHONPATH=. python3 -m absurd_ops.cli init
PYTHONPATH=. python3 -m absurd_ops.cli status          # ops state
PYTHONPATH=. python3 -m absurd_ops.cli dashboard       # http://127.0.0.1:8899
PYTHONPATH=. python3 -m absurd_ops.cli daily           # run the newsroom once
```

## The pipeline (runs twice daily via systemd timer)

```
feeds ──▶ trend_monitor ──▶ opportunity_analyst ──▶ writer (Devin)
                                                          │
social_agent ◀── seo_editor ◀── safety_editor ◀── comedy_editor
     │
     ▼
publishing_agent ──▶ git commit/push ──▶ Vercel deploy ──▶ URL verify
     │                                                          │
     ▼                                                          ▼
growth_analyst + revenue_strategist      social_poster ──▶ Bluesky/Mastodon/Threads
(metrics, reports)                       (opt-in via ABSURD_SOCIAL_POST=1)
```

Quality gates: an idea must score ≥ 6.5/10 to reach the writer; a draft must
score ≥ 7/10 with the comedy editor AND pass the safety editor (deterministic
checks + a Devin review) before publication. When no story is strong enough,
nothing publishes — that is a feature.

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
- [docs/AGENTS.md](docs/AGENTS.md) — the ten agents
- [docs/OPERATIONS.md](docs/OPERATIONS.md) — runbook
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — GitHub → Vercel
- [docs/MONETIZATION.md](docs/MONETIZATION.md) — revenue roadmap
- [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) — env vars
