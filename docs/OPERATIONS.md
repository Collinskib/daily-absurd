# Operations Runbook

## Services

```bash
ops/install-services.sh          # install + enable everything
systemctl --user status absurd-pipeline.timer
systemctl --user status absurd-dashboard.service
journalctl --user -u absurd-pipeline.service -f     # pipeline logs
systemctl --user list-timers --all | grep absurd
```

- `absurd-pipeline.timer` — runs the full newsroom at **06:30 and 16:30**
  daily (`Persistent=true` catches up after downtime).
- `absurd-dashboard.service` — ops room at **http://127.0.0.1:8899**
  (loopback only; `GET /api/status` for JSON).

## Manual control

```bash
cd agents
PYTHONPATH=. python3 -m absurd_ops.cli daily            # full run
PYTHONPATH=. python3 -m absurd_ops.cli run-agent writer # one stage
PYTHONPATH=. python3 -m absurd_ops.cli status           # JSON snapshot
```

## Knobs

| Env var | Effect |
|---|---|
| `ABSURD_DEVIN_ENABLED=0` | research-only mode — no Devin sessions, nothing publishes |
| `ABSURD_GIT_PUSH=0` | stage articles locally, never push |
| `ABSURD_MAX_ARTICLES=4` | cap articles per run |
| `ABSURD_MIN_IDEA_SCORE` / `ABSURD_MIN_COMEDY_SCORE` | quality thresholds |
| `DEVIN_TIMEOUT_SECONDS=900` | per-session cap |

## Recovery

- **Stuck draft**: `sqlite3 agents/state/absurd.db "UPDATE drafts SET status='written' WHERE slug='…'"` to force re-review, or delete the row.
- **Bad publish**: `git revert` the publish commit and push — Vercel rolls back.
- **Dashboard down**: `systemctl --user restart absurd-dashboard`.
- **Everything is on fire**: `ABSURD_DEVIN_ENABLED=0` + `systemctl --user stop absurd-pipeline.timer` freezes output; content already live stays live.

## Weekly rhythm

The growth analyst appends metrics each run; review `agents/state/growth-report.json`
and the dashboard. A human should skim top performers and flag weak categories —
the agents follow the data, they don't decide the brand.
