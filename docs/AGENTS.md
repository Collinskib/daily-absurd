# The Ten Agents

Every agent: defined input/output, `agent_runs` logging, bounded retries via
the tasks table where applicable, idempotent (safe to re-run).

| # | Agent | Staffing | Input → Output |
|---|-------|----------|----------------|
| 1 | **Global Trend Monitor** | Python | RSS/Atom feeds → `trends` rows (deduped by URL) |
| 2 | **Satire Opportunity Analyst** | Python + 1 Devin session | trends → scored `story_ideas` with angles, category, risk screen |
| 3 | **Satirical Writer** | Devin (`devin -p`) | idea + trend context → draft article JSON |
| 4 | **Comedy Editor** | Devin | draft → verdict JSON (score, notes, rewrite instructions) |
| 5 | **Factual Context & Safety Editor** | Python + Devin | draft → pass/fail; deterministic rules + editorial review |
| 6 | **SEO Editor** | Python | draft → SEO-complete article (title, description, slug, tags, art) |
| 7 | **Social Media Creative** | Python | article → per-platform pack + SVG share card (never auto-posts) |
| 8 | **Publishing Agent** | Python + git | approved draft → article JSON, commit, push, URL verify |
| 9 | **Growth Analyst** | Python | DB + subscriber ledger → metrics rows + weekly report |
| 10 | **Revenue Strategist** | Python | monetization readiness ledger (prepared, never activated) |

## Gates

- Idea → draft: `score ≥ ABSURD_MIN_IDEA_SCORE` (6.5)
- Draft → approved: comedy `pass` at `≥ 7.0` AND safety `pass`
  (deterministic + Devin). Inconclusive safety = fail.
- Approved → published: git push success + live URL 200.

## Safety invariants (enforced in code + prompts)

- No invented quotes attributed to real identifiable people.
- No fabricated allegations about real people.
- No fake emergency alerts / official statements (pattern-blocked).
- Sensitive-topic terms escalate to fail (pattern-blocked).
- `sourceEvent` required on every article; missing = fail.
- SATIRE badge on every article page; `SatiricalArticle` JSON-LD;
  `satire-disclosure` meta site-wide.

## Cost shape

Devin sessions per article: writer (1) + comedy review (1) + safety review
(1) + at most one rewrite. Analyst angle-pass: 1 per run (batched).
Everything else is free local compute.
