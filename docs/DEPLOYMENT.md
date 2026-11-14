# Deployment

## GitHub

```bash
cd /home/collins/Documents/daily-absurd
gh repo create daily-absurd --public --source . --push
```

Pushes to `main` deploy production; PRs deploy previews (Vercel Git
integration). The publishing agent pushes directly to `main` — that is the
point: articles are content, not code changes.

## Vercel

The Vercel project root is `web/`. First deploy (from the machine, already
authenticated):

```bash
cd web
vercel --prod --yes          # creates project 'daily-absurd'
```

Production URL: https://daily-absurd.vercel.app (verify with
`curl -I https://daily-absurd.vercel.app`).

### Environment variables (Vercel project settings)

| Var | Purpose | Required |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | canonical URL | yes |
| `NEWSLETTER_REPO` | `owner/repo` for dispatch | for newsletter |
| `NEWSLETTER_DISPATCH_TOKEN` | GitHub PAT, `repo` scope | for newsletter |
| `NEWSLETTER_SECRET` | HMAC for unsubscribe links | for newsletter |

## Local services

`ops/install-services.sh` installs `--user` units; linger is enabled so they
survive logout. `SITE_URL` inside `absurd-pipeline.service` must match the
production URL so the publish verifier checks the right host.
