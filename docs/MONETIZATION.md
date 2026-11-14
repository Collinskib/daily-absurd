# Monetization Roadmap

**Status: infrastructure prepared, nothing activated.** No paid service is
switched on without explicit approval; editorial independence is not for sale.

| Stream | Readiness | Blocked on |
|---|---|---|
| Display ads | Ad slots reserved in layout (`data-ad` zones, none rendered); privacy policy already states no behavioural ads | Network application (needs traffic history) + approval |
| Newsletter sponsorship | Subscriber pipeline + unsubscribe + ledger working; rate card slot in dashboard | ESP integration (Resend/Loops key) + list ≥1k |
| Premium membership | Content is static; member-gated tier needs auth | Payment provider approval (Stripe) |
| Merchandise | Deterministic SVG share-card art doubles as merch designs | Print-on-demand partner |
| Affiliate | Disclosure language in editorial policy | Partner programs (book/merch affiliates fit satire best) |
| Content licensing | Original corpus growing daily | Syndication outreach |

## Sequence

1. Grow organic + newsletter audience (agents already optimise for this).
2. At ~10k monthly readers: apply to an ad network that accepts satire and
   international traffic (e.g. Google AdSense alternatives like Raptive/Ezoic
   tier permitting); serve via the reserved slots only.
3. At ~1k subscribers: first newsletter sponsorship slot.
4. Merchandise once a headline goes viral — the share-card pipeline already
   produces the art.

The revenue strategist agent writes readiness state to the `metrics` table
each run; see the ops dashboard.
