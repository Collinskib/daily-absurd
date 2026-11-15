# Environment Variables

See `.env.example` for the full template.

## Required

| Var | Where | What |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | Vercel | canonical site URL (sitemap, OG, RSS) |
| `SITE_URL` | pipeline service | used by the publish verifier |

## Optional

| Var | Where | What |
|---|---|---|
| `NEWSLETTER_*` | Vercel | newsletter dispatch + unsubscribe signing |
| `ABSURD_*` | services | pipeline tuning (see OPERATIONS.md) |
| `DEVIN_TIMEOUT_SECONDS` | services | Devin session cap |

## Traffic metrics

| Var | Where | What |
|---|---|---|
| `ABSURD_READER_TARGET` | pipeline service | monthly visitor goal (default 10000) |
| `ABSURD_VERCEL_TOKEN` | pipeline service | optional; falls back to local `vercel` CLI auth |
| `ABSURD_GSC_SITE` | pipeline service | Search Console property URL |
| `ABSURD_GSC_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | pipeline service | OAuth creds from `python3 -m absurd_ops.cli gsc-auth` |

The pipeline service loads `.env` via `EnvironmentFile=` — put the GSC
values there, then `systemctl --user daemon-reload`.

No secrets are committed. `.env*` files are gitignored.
