from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import db


def traced(name: str) -> Callable[[Callable[..., Any]], Callable[..., dict]]:
    """Wrap an agent run with agent_runs logging."""
    def deco(fn: Callable[..., Any]) -> Callable[..., dict]:
        def wrapper(*args: Any, **kwargs: Any) -> dict:
            rid = db.log_run(name)
            try:
                result = fn(*args, **kwargs)
                detail = result.get("detail", "") if isinstance(result, dict) else ""
                db.finish_run(rid, "ok", str(detail)[:2000])
                return {"agent": name, "ok": True, **(result if isinstance(result, dict) else {})}
            except Exception as exc:  # noqa: BLE001 - agents must not crash the pipeline
                db.finish_run(rid, "error", str(exc)[:2000])
                return {"agent": name, "ok": False, "error": str(exc)}
        return wrapper
    return deco
