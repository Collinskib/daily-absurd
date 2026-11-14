from __future__ import annotations

import argparse
import json
import sys

from . import db, pipeline
from . import agents as A

AGENTS = {name: getattr(A, name) for name in A.__all__}


def main() -> int:
    p = argparse.ArgumentParser(prog="absurd", description="Daily Absurd ops")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("daily")
    sub.add_parser("status")
    a = sub.add_parser("run-agent"); a.add_argument("name", choices=sorted(AGENTS))
    sub.add_parser("dashboard")

    args = p.parse_args()
    db.init()

    if args.cmd == "init":
        print(f"db initialised at {db.config.DB_PATH}")
        return 0
    if args.cmd == "daily":
        print(json.dumps(pipeline.daily(), indent=2)[:8000])
        return 0
    if args.cmd == "status":
        print(json.dumps(pipeline.status(), indent=2))
        return 0
    if args.cmd == "run-agent":
        print(json.dumps(AGENTS[args.name](), indent=2))
        return 0
    if args.cmd == "dashboard":
        from .dashboard.server import serve
        serve()
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
