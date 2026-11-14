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

No secrets are committed. `.env*` files are gitignored.
