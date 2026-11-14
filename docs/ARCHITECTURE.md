# Architecture

## Overview

The Daily Absurd is two systems joined by git:

1. **The publication** (`web/`) — a fully static-rendered Next.js site on
   Vercel. Articles are JSON documents committed to `web/content/articles/`.
   Git is the CMS: every publish is a commit; every deploy is a Vercel build
   triggered by push.
2. **The newsroom** (`agents/`) — a stdlib-only Python package (`absurd_ops`)
   running on the local Linux host under `systemd --user`. It owns a SQLite
   database (`agents/state/absurd.db`), an on-disk editorial queue, and ten
   specialised agents.

```
┌──────────────────────── LOCAL LINUX HOST ───────────────────────────┐
│                                                                     │
│  systemd timer ──▶ absurd_ops.cli daily                             │
│         │                                                           │
│         ▼                                                           │
│  trend_monitor ─ feeds/RSS (BBC, Guardian, AJ, Reddit, HN, DW…)      │
│         │  trends table (SQLite)                                    │
│         ▼                                                           │
│  opportunity_analyst ─ heuristic score + 1 batched Devin session    │
│         │  story_ideas (score ≥ 6.5)                                │
│         ▼                                                           │
│  writer ─ `devin -p` session per idea ─▶ queue/drafts/*.json        │
│         ▼                                                           │
│  comedy_editor ─ `devin -p` verdict (+1 rewrite max)                │
│         ▼                                                           │
│  safety_editor ─ deterministic checks + `devin -p` review           │
│         ▼                                                           │
│  seo_editor ─ mechanical SEO fixes (stdlib)                         │
│         ▼                                                           │
│  social_agent ─ per-platform packs + SVG share cards (stdlib)       │
│         ▼                                                           │
│  publishing_agent ─ write article JSON → git commit → git push      │
│         ▼                                                           │
│  growth_analyst / revenue_strategist ─ metrics + ledgers            │
│                                                                     │
│  absurd-dashboard.service ─ localhost:8899 ops room                 │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ git push
                                   ▼
                          ┌─────────────────┐
                          │  GitHub (main)  │
                          └────────┬────────┘
                                   │ webhook
                                   ▼
                          ┌─────────────────┐     ┌────────────────┐
                          │  Vercel build   │────▶│ dailyabsurd    │
                          └─────────────────┘     │ production URL │
                                                 └────────────────┘
```

## Why git is the CMS

The prompt asked for publishing that "generates article files, commits to
GitHub, verifies Vercel deployment". Committing articles makes publishing
atomic, reviewable in `git log`, trivially rollback-able (`git revert`), and
keeps Vercel deploys deterministic — the site has zero runtime database
dependency.

## Why Devin is the editorial staff

No external LLM key is required: the quality roles (writer, comedy editor,
safety editor) spawn bounded `devin -p` sessions with a prompt file and an
expected output file. Cheap/deterministic work (scoring pre-filter, SEO
repairs, social assembly, publishing) stays in Python so Devin sessions are
only spent where judgement matters.

## Data stores

| Store | Contents |
|---|---|
| `agents/state/absurd.db` | trends, story_ideas, drafts, reviews, published, social_assets, metrics, agent_runs, tasks, subscribers |
| `agents/queue/` | writing briefs, draft JSON, review verdicts, social packs |
| `web/content/articles/*.json` | the published corpus (in git) |
| `web/content/subscribers.ndjson` | newsletter subscriber ledger (GitHub Actions append) |

## Failure modes

- A Devin session times out or produces invalid JSON → stage skipped for
  that item; the idea/draft stays queued for the next run; `agent_runs`
  records the error on the dashboard.
- Safety review is inconclusive → verdict defaults to **fail** (absent
  evidence is never a pass).
- Push fails → article stays `approved`, not `published`; retried next run.
- Verification of the live URL fails → `deployed=0` recorded, so the
  dashboard shows the discrepancy.

## Newsletter plumbing

Site form → `POST /api/newsletter` → GitHub `repository_dispatch`
(`newsletter-signup`/`newsletter-unsubscribe`) → `newsletter.yml` workflow
appends to `web/content/subscribers.ndjson` → local `sync_subscribers()`
ingests the ledger into SQLite. Unsubscribe links are HMAC-signed
(`NEWSLETTER_SECRET`). An ESP (Resend/Loops) can replace the dispatch path
later without changing the site.
