"""External traffic metrics — Vercel Web Analytics + Google Search Console.

Read-only readers so the growth analyst can steer toward the monthly
reader target. Stdlib only, plain HTTPS:

- Vercel Web Analytics REST API. Bearer token comes from
  ABSURD_VERCEL_TOKEN / VERCEL_TOKEN, falling back to the local Vercel CLI
  auth (~/.local/share/com.vercel.cli/auth.json). Project/team IDs come
  from web/.vercel/project.json (or ABSURD_VERCEL_PROJECT_ID /
  ABSURD_VERCEL_TEAM_ID).
- Search Console searchAnalytics API. Auth is an OAuth refresh-token
  exchange — no crypto needed, so stdlib suffices. Credentials come from
  ABSURD_GSC_* env vars, produced once by `python3 -m absurd_ops.cli
  gsc-auth` (see docs/OPERATIONS.md).
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import config

VERCEL_API = "https://api.vercel.com"
GSC_TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_API = "https://searchconsole.googleapis.com"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"


class MetricsError(RuntimeError):
    pass


def _request(url: str, token: str | None = None, payload: dict | None = None,
             timeout: int = 20) -> dict:
    headers = {"User-Agent": config.USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:300]
        raise MetricsError(f"HTTP {e.code} from {url}: {detail}") from e
    except Exception as e:
        raise MetricsError(f"{url}: {e}") from e


def _get(url: str, params: dict, token: str) -> dict:
    sep = "&" if "?" in url else "?"
    return _request(f"{url}{sep}{urllib.parse.urlencode(params)}", token)


# --- Vercel Web Analytics -----------------------------------------------------

def vercel_token() -> str:
    if config.VERCEL_TOKEN:
        return config.VERCEL_TOKEN
    auth = Path.home() / ".local" / "share" / "com.vercel.cli" / "auth.json"
    try:
        data = json.loads(auth.read_text())
    except OSError as e:
        raise MetricsError(
            "no Vercel token: set ABSURD_VERCEL_TOKEN or run `vercel login`"
        ) from e
    token = data.get("token", "")
    if not token:
        raise MetricsError(f"{auth} has no token — run `vercel login`")
    return token


def vercel_scope() -> tuple[str, str]:
    """(project_id, team_id) for the deployment in web/.vercel/project.json."""
    proj = config.VERCEL_PROJECT_ID
    team = config.VERCEL_TEAM_ID
    meta = config.WEB_DIR / ".vercel" / "project.json"
    if not (proj and team) and meta.exists():
        try:
            data = json.loads(meta.read_text())
        except json.JSONDecodeError:
            data = {}
        proj = proj or data.get("projectId", "")
        team = team or data.get("orgId", "")
    if not proj:
        raise MetricsError("no Vercel project id — link the project or set "
                           "ABSURD_VERCEL_PROJECT_ID")
    return proj, team


def _vercel_params(project: str, team: str, extra: dict) -> dict:
    params = {"projectId": project}
    if team:
        params["teamId"] = team
    return {**params, **extra}


def vercel_traffic(since: str, until: str) -> dict:
    """Total visitors + pageviews (production) between two dates."""
    project, team = vercel_scope()
    res = _get(
        f"{VERCEL_API}/v1/query/web-analytics/visits/count",
        _vercel_params(project, team, {"since": since, "until": until}),
        vercel_token(),
    )
    data = res.get("data") or {}
    return {"visitors": int(data.get("visitors", 0)),
            "pageviews": int(data.get("pageviews", 0))}


def vercel_breakdown(dimension: str, since: str, until: str,
                     limit: int = 10) -> list[dict]:
    """Aggregate pageviews/visitors grouped by a dimension (day, requestPath,
    referrerHostname, ...). Row shape is normalised to
    {"key": <dim value>, "visitors": n, "pageviews": n}."""
    project, team = vercel_scope()
    res = _get(
        f"{VERCEL_API}/v1/query/web-analytics/visits/aggregate",
        _vercel_params(project, team, {
            "by": dimension, "since": since, "until": until, "limit": limit,
        }),
        vercel_token(),
    )
    rows = []
    for row in res.get("data") or []:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        if isinstance(key, dict):
            key = key.get(dimension) or next(iter(key.values()), "")
        if key is None:
            key = row.get(dimension, "")
        rows.append({
            "key": key,
            "visitors": int(row.get("visitors", 0)),
            "pageviews": int(row.get("pageviews", 0)),
        })
    return rows


# --- Google Search Console ----------------------------------------------------

def gsc_configured() -> bool:
    return bool(config.GSC_SITE_URL and config.GSC_CLIENT_ID
                and config.GSC_CLIENT_SECRET and config.GSC_REFRESH_TOKEN)


def gsc_access_token() -> str:
    res = _request(GSC_TOKEN_URL, payload={
        "client_id": config.GSC_CLIENT_ID,
        "client_secret": config.GSC_CLIENT_SECRET,
        "refresh_token": config.GSC_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    })
    token = res.get("access_token")
    if not token:
        raise MetricsError("GSC token exchange returned no access_token")
    return token


def gsc_search_analytics(start: str, end: str, dimensions: list[str],
                         row_limit: int = 25) -> list[dict]:
    site = urllib.parse.quote(config.GSC_SITE_URL, safe="")
    res = _request(
        f"{GSC_API}/v1/sites/{site}/searchAnalytics/query",
        token=gsc_access_token(),
        payload={
            "startDate": start, "endDate": end,
            "dimensions": dimensions, "rowLimit": row_limit,
        },
    )
    return res.get("rows") or []


# --- Orchestration ------------------------------------------------------------

def _month_bounds() -> tuple[str, str, int]:
    """(first-of-month, tomorrow, days-left-in-month) in UTC."""
    tm = time.gmtime()
    since = f"{tm.tm_year:04d}-{tm.tm_mon:02d}-01"
    until = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 86400))
    if tm.tm_mon == 12:
        nxt = time.struct_time((tm.tm_year + 1, 1, 1, 0, 0, 0, 0, 1, -1))
    else:
        nxt = time.struct_time((tm.tm_year, tm.tm_mon + 1, 1, 0, 0, 0, 0, 1, -1))
    days_left = int((time.mktime(nxt) - time.time()) / 86400)
    return since, until, max(days_left, 0)


def _days_ago(n: int) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() - n * 86400))


def collect() -> dict:
    """One traffic snapshot. Individual source failures are captured as
    {"error": ...} so a broken integration never sinks the pipeline run."""
    since_m, until_m, days_left = _month_bounds()
    out: dict[str, Any] = {"generated_at": time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    try:
        vercel = vercel_traffic(since_m, until_m)
        vercel["by_day"] = vercel_breakdown("day", _days_ago(28), until_m, limit=28)
        vercel["top_pages"] = vercel_breakdown("requestPath", _days_ago(28),
                                             until_m, limit=10)
        vercel["top_referrers"] = vercel_breakdown("referrerHostname",
                                                 _days_ago(28), until_m, limit=10)
        out["vercel"] = vercel
    except MetricsError as e:
        out["vercel"] = {"error": str(e)}

    if gsc_configured():
        try:
            start, end = _days_ago(28), _days_ago(1)
            rows = gsc_search_analytics(start, end, ["date"], row_limit=28)
            clicks = sum(r.get("clicks", 0) for r in rows)
            imps = sum(r.get("impressions", 0) for r in rows)
            out["search_console"] = {
                "clicks_28d": clicks,
                "impressions_28d": imps,
                "top_queries": gsc_search_analytics(start, end, ["query"], 10),
                "top_pages": gsc_search_analytics(start, end, ["page"], 10),
            }
        except MetricsError as e:
            out["search_console"] = {"error": str(e)}
    else:
        out["search_console"] = {"configured": False}

    mtd = (out.get("vercel") or {}).get("visitors", 0)
    target = config.MONTHLY_READER_TARGET
    elapsed_days = max(int(time.gmtime().tm_mday), 1)
    out["target"] = {
        "monthly_readers": target,
        "visitors_mtd": mtd,
        "pct_of_target": round(100 * mtd / target, 1) if target else 0,
        "days_left_in_month": days_left,
        "required_daily_pace": round(max(target - mtd, 0) / max(days_left, 1), 1),
        "current_daily_pace": round(mtd / elapsed_days, 1),
    }
    return out
