"""External traffic metrics — Vercel Web Analytics + Google Search Console.

Read-only readers so the growth analyst can steer toward the monthly
reader target. Stdlib only, plain HTTPS:

- Vercel Web Analytics REST API. Bearer token comes from
  ABSURD_VERCEL_TOKEN / VERCEL_TOKEN, falling back to the local Vercel CLI
  auth (~/.local/share/com.vercel.cli/auth.json). Project/team IDs come
  from web/.vercel/project.json (or ABSURD_VERCEL_PROJECT_ID /
  ABSURD_VERCEL_TEAM_ID).
- Search Console searchAnalytics API. Preferred auth is a
  service-account JWT grant (ABSURD_GSC_SA_PATH, RS256 signed with
  `cryptography` or `openssl`); the OAuth refresh-token exchange
  (ABSURD_GSC_* vars from `cli gsc-auth`) remains as fallback.
"""
from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import config

VERCEL_API = "https://api.vercel.com"
GSC_TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_API = "https://www.googleapis.com/webmasters/v3"
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


def _post_form(url: str, fields: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(fields).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": config.USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise MetricsError(f"HTTP {e.code} from {url}: {e.read().decode()[:300]}") from e
    except Exception as e:
        raise MetricsError(f"{url}: {e}") from e


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
            # Dimensions arrive as their own field; time buckets use "timestamp".
            key = row.get(dimension) or row.get("timestamp", "")
        rows.append({
            "key": key,
            "visitors": int(row.get("visitors", 0)),
            "pageviews": int(row.get("pageviews", 0)),
        })
    return rows


# --- Google Search Console ----------------------------------------------------

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _sign_rs256(msg: bytes, key_pem: str) -> bytes:
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        key = serialization.load_pem_private_key(key_pem.encode(), password=None)
        return key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    except ImportError:
        # openssl is present on any system running the pipeline.
        with tempfile.TemporaryDirectory() as td:
            kp = Path(td) / "k.pem"
            kp.write_text(key_pem)
            mp = Path(td) / "m"
            mp.write_bytes(msg)
            return subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", str(kp), str(mp)],
                capture_output=True, check=True,
            ).stdout


def _sa_assertion(sa: dict) -> str:
    """JWT for the service-account grant (RFC 7523, RS256)."""
    now = int(time.time())
    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = _b64url(json.dumps({
        "iss": sa["client_email"],
        "scope": GSC_SCOPE,
        "aud": GSC_TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }).encode())
    sig = _b64url(_sign_rs256(f"{header}.{claims}".encode(), sa["private_key"]))
    return f"{header}.{claims}.{sig}"


def _sa_configured() -> bool:
    return bool(config.GSC_SITE_URL and config.GSC_SA_PATH
                and Path(config.GSC_SA_PATH).expanduser().exists())


def gsc_configured() -> bool:
    if _sa_configured():
        return True
    return bool(config.GSC_SITE_URL and config.GSC_CLIENT_ID
                and config.GSC_CLIENT_SECRET and config.GSC_REFRESH_TOKEN)


def gsc_access_token() -> str:
    if _sa_configured():
        sa_path = Path(config.GSC_SA_PATH).expanduser()
        sa = json.loads(sa_path.read_text())
        res = _post_form(GSC_TOKEN_URL, {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": _sa_assertion(sa),
        })
    else:
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
        f"{GSC_API}/sites/{site}/searchAnalytics/query",
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


def traffic_brief_section() -> str:
    """Compact traffic summary for Devin prompts — what's pulling readers.

    Read from the latest growth-report.json; empty/absent fields degrade
    to the bare target line so prompts stay useful on day one.
    """
    lines = [f"READER TARGET: {config.MONTHLY_READER_TARGET} visitors/month."]
    report = config.STATE_DIR / "growth-report.json"
    try:
        traffic = json.loads(report.read_text()).get("traffic") or {}
    except (OSError, json.JSONDecodeError):
        traffic = {}
    target = traffic.get("target") or {}
    if target:
        lines[0] += (
            f" Month-to-date {target.get('visitors_mtd', 0)} "
            f"({target.get('pct_of_target', 0)}%) — pace needed "
            f"~{target.get('required_daily_pace', '?')}/day for "
            f"{target.get('days_left_in_month', '?')} more days."
        )
    vercel = traffic.get("vercel") or {}
    gsc = traffic.get("search_console") or {}
    pages = [r["key"] for r in vercel.get("top_pages", []) if r.get("key")]
    refs = [r["key"] for r in vercel.get("top_referrers", []) if r.get("key")]
    queries = [(r.get("keys") or [""])[0] for r in gsc.get("top_queries", [])]
    if pages:
        lines.append("MOST-READ PAGES: " + "; ".join(pages[:5]))
    if refs:
        lines.append("TOP REFERRERS: " + "; ".join(refs[:5]))
    if any(queries):
        lines.append("TOP SEARCH QUERIES: " + "; ".join(q for q in queries if q)[:400])
    lines.append(
        "Weight shareability for premises that fit the referrers and "
        "queries above; favour topics matching the most-read pages."
    )
    return "\n".join(lines)


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
