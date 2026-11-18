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
| `ABSURD_GSC_SA_PATH` | pipeline service | service-account JSON (default: shared `~/.config/claude-seo/service_account.json`) |
| `ABSURD_GSC_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | pipeline service | OAuth creds from `python3 -m absurd_ops.cli gsc-auth` (fallback) |

## Social posting

| Var | Where | What |
|---|---|---|
| `ABSURD_SOCIAL_POST` | pipeline service | `1` arms real posting; unset/`0` = dry-run |
| `ABSURD_SOCIAL_MAX_PER_RUN` | pipeline service | articles processed per run (default 2) |
| `ABSURD_BSKY_HANDLE` / `ABSURD_BSKY_APP_PASSWORD` | pipeline service | Bluesky handle + app password |
| `ABSURD_MASTO_INSTANCE` / `ABSURD_MASTO_TOKEN` | pipeline service | Mastodon instance URL + access token |
| `ABSURD_THREADS_USER_ID` / `ABSURD_THREADS_TOKEN` | pipeline service | Threads user ID + long-lived token (`threads_content_publish` scope) |

Each channel activates only when its credential pair is present. Posts only
go out for articles with `deployed=1`; every attempt lands in the
`social_posts` table (unique per slug+channel), so failures retry next run
and nothing double-posts.

The pipeline service loads `.env` via `EnvironmentFile=` — put the GSC
values there, then `systemctl --user daemon-reload`.

No secrets are committed. `.env*` files are gitignored.
