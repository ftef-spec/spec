# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Review periods (CONTRIBUTING.md) as a commit status, so that a pull request cannot merge inside its period.

    python tools/review_period.py --repo ftef-spec/spec --all            # set the status on every open pull request
    python tools/review_period.py --repo ftef-spec/spec --pr 52 --dry-run  # print what it would set, write nothing

The kind comes from the pull request's `kind:` label. A normative change counts from the earliest linked "Proposal:"
issue (Closes, Fixes, Resolves or Refs #N in the body), unless the label "review: from PR" says the pull request adds a
requirement the issue does not describe; it also needs a record in decisions/. Everything else counts from the pull
request. A line "Review period restarted: <UTC time>" in the body (for a push that adds a requirement) moves the start
to that time if it is later. The check reads the GitHub API only; it never runs code from the pull request.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta

CONTEXT = "review-period"
PERIODS = {"kind: normative": timedelta(days=7), "kind: fix": timedelta(hours=72),
           "kind: tooling": timedelta(hours=72), "kind: editorial": timedelta(hours=24)}
FROM_PR = "review: from PR"
BOTS = {"dependabot[bot]": "kind: tooling"}       # dependency bumps change tooling, never the specification
RESTART = re.compile(r"^Review period restarted: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z)\s*$", re.MULTILINE)
LINK = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\b:?\s+#(\d+)", re.IGNORECASE)
API = "https://api.github.com"


def _t(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def linked_issues(body: str | None) -> list[int]:
    return sorted({int(n) for n in LINK.findall(body or "")})


def kind_of(pr: dict) -> tuple[str | None, str | None]:
    """The pull request's kind label, or an error saying what is wrong."""
    kinds = [lb["name"] for lb in pr.get("labels", []) if lb["name"] in PERIODS]
    if len(kinds) > 1:
        return None, "more than one kind label: " + ", ".join(sorted(kinds))
    if kinds:
        return kinds[0], None
    bot = BOTS.get(pr.get("user", {}).get("login", ""))
    if bot:
        return bot, None
    return None, "no kind label; add one of: " + ", ".join(PERIODS)


def evaluate(pr: dict, issues: dict[int, dict], files: list[str], now: datetime) -> tuple[str, str]:
    """(state, description) for the commit status: success, pending or failure."""
    kind, err = kind_of(pr)
    if err:
        return "failure", err
    start = _t(pr["created_at"])
    if kind == "kind: normative":
        if not any(f.startswith("decisions/") for f in files):
            return "failure", "a normative change needs a record in decisions/"
        labels = {lb["name"] for lb in pr.get("labels", [])}
        if FROM_PR not in labels:
            opened = [_t(issues[n]["created_at"]) for n in linked_issues(pr.get("body")) if n in issues
                      and issues[n]["title"].startswith("Proposal:") and "pull_request" not in issues[n]]
            if opened:
                start = min([start, *opened])     # the change was first public when the earlier of the two opened
    restarts = [_t(m) for m in RESTART.findall(pr.get("body") or "")]
    if restarts:
        start = max([start, *restarts])         # a push that added a requirement restarts the period
    end = start + PERIODS[kind]
    name = kind.removeprefix("kind: ")
    if now >= end:
        return "success", f"{name}: review period ended {end:%Y-%m-%d %H:%M} UTC"
    return "pending", f"{name}: review period ends {end:%Y-%m-%d %H:%M} UTC"


# --- GitHub API (stdlib only) -------------------------------------------------------------------------------------
def _call(method: str, path: str, token: str, body: dict | None = None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "ftef-review-period"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def _pages(path: str, token: str) -> list:
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        chunk = _call("GET", f"{path}{sep}per_page=100&page={page}", token)
        out += chunk
        if len(chunk) < 100:
            return out
        page += 1


def run(repo: str, numbers: list[int] | None, token: str, dry_run: bool, now: datetime) -> int:
    prs = [_call("GET", f"/repos/{repo}/pulls/{n}", token) for n in numbers] if numbers \
        else _pages(f"/repos/{repo}/pulls?state=open", token)
    for pr in prs:
        files = [f["filename"] for f in _pages(f"/repos/{repo}/pulls/{pr['number']}/files", token)]
        issues = {}
        for n in linked_issues(pr.get("body")):
            with contextlib.suppress(urllib.error.HTTPError):  # a link to nothing does not start the clock
                issues[n] = _call("GET", f"/repos/{repo}/issues/{n}", token)
        state, desc = evaluate(pr, issues, files, now)
        print(f"#{pr['number']:<4} {state:<8} {desc}")
        if not dry_run:
            _call("POST", f"/repos/{repo}/statuses/{pr['head']['sha']}", token,
                  {"state": state, "context": CONTEXT, "description": desc[:140],
                   "target_url": f"https://github.com/{repo}/blob/main/CONTRIBUTING.md#changes"})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pr", type=int, action="append")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the statuses, write nothing")
    a = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 2
    return run(a.repo, a.pr, token, a.dry_run, datetime.now(UTC))


if __name__ == "__main__":
    sys.exit(main())
