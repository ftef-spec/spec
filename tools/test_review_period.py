# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for review_period.py: fixtures only, no network.  python -m unittest discover -s tools -p "test_*.py" """
from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_period import evaluate, kind_of, linked_issues

OPENED = "2026-10-23T08:00:00Z"


def pr(labels=(), body="", login="maintainer", created=OPENED):
    return {"number": 1, "created_at": created, "labels": [{"name": n} for n in labels], "body": body,
            "user": {"login": login}, "head": {"sha": "0" * 40}}


def at(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)


PROPOSAL = {16: {"title": "Proposal: freshness for date-only sources", "created_at": "2026-10-15T10:00:00Z"}}
DECISION = ["decisions/0011-date-only-sources.md", "spec/ftef.md"]


class Kinds(unittest.TestCase):
    def test_no_label_fails_and_names_the_labels(self):
        state, desc = evaluate(pr(), {}, [], at("2026-11-30T00:00:00Z"))
        self.assertEqual(state, "failure")
        self.assertIn("kind: normative", desc)

    def test_two_kind_labels_fail(self):
        self.assertIsNone(kind_of(pr(["kind: fix", "kind: editorial"]))[0])

    def test_dependabot_is_tooling(self):
        self.assertEqual(kind_of(pr(login="dependabot[bot]"))[0], "kind: tooling")

    def test_other_labels_are_ignored(self):
        self.assertEqual(kind_of(pr(["bug", "kind: fix"]))[0], "kind: fix")


class Periods(unittest.TestCase):
    def test_editorial_24h(self):
        self.assertEqual(evaluate(pr(["kind: editorial"]), {}, [], at("2026-10-24T07:59:00Z"))[0], "pending")
        self.assertEqual(evaluate(pr(["kind: editorial"]), {}, [], at("2026-10-24T08:00:00Z"))[0], "success")

    def test_fix_and_tooling_72h(self):
        for k in ("kind: fix", "kind: tooling"):
            self.assertEqual(evaluate(pr([k]), {}, [], at("2026-10-26T07:59:00Z"))[0], "pending")
            self.assertEqual(evaluate(pr([k]), {}, [], at("2026-10-26T08:00:00Z"))[0], "success")

    def test_pending_names_the_end(self):
        self.assertIn("ends 2026-10-26 08:00 UTC", evaluate(pr(["kind: fix"]), {}, [], at(OPENED))[1])


class Normative(unittest.TestCase):
    def test_needs_a_decision_record(self):
        state, desc = evaluate(pr(["kind: normative"]), {}, ["spec/ftef.md"], at("2026-12-01T00:00:00Z"))
        self.assertEqual(state, "failure")
        self.assertIn("decisions/", desc)

    def test_counts_from_pr_without_proposal_issue(self):
        p = pr(["kind: normative"])
        self.assertEqual(evaluate(p, {}, DECISION, at("2026-10-30T07:59:00Z"))[0], "pending")
        self.assertEqual(evaluate(p, {}, DECISION, at("2026-10-30T08:00:00Z"))[0], "success")

    def test_counts_from_linked_proposal_issue(self):
        p = pr(["kind: normative"], body="Closes #16")
        self.assertEqual(evaluate(p, PROPOSAL, DECISION, at(OPENED))[0], "success")      # issue opened 2026-10-15

    def test_refs_keyword_and_colon(self):
        self.assertEqual(linked_issues("Refs: #16, fixes #3 and Resolves #40; see #19"), [3, 16, 40])

    def test_from_pr_label_restarts_from_the_pr(self):
        p = pr(["kind: normative", "review: from PR"], body="Closes #16")
        self.assertEqual(evaluate(p, PROPOSAL, DECISION, at(OPENED))[0], "pending")

    def test_non_proposal_issue_does_not_start_the_clock(self):
        p = pr(["kind: normative"], body="Closes #19")
        roadmap = {19: {"title": "Roadmap to 0.2.0", "created_at": "2026-10-01T00:00:00Z"}}
        self.assertEqual(evaluate(p, roadmap, DECISION, at(OPENED))[0], "pending")

    def test_a_pull_request_is_not_a_proposal_issue(self):
        p = pr(["kind: normative"], body="Refs #16")
        pull = {16: dict(PROPOSAL[16], pull_request={"url": "x"})}
        self.assertEqual(evaluate(p, pull, DECISION, at(OPENED))[0], "pending")

    def test_restart_line_moves_the_start(self):
        p = pr(["kind: normative"], body="Part of #19\nReview period restarted: 2026-10-23T10:00Z\n")
        self.assertIn("ends 2026-10-30 10:00 UTC", evaluate(p, {}, DECISION, at(OPENED))[1])

    def test_restart_line_never_moves_the_start_earlier(self):
        p = pr(["kind: fix"], body="Review period restarted: 2026-10-01T00:00Z")
        self.assertIn("ends 2026-10-26 08:00 UTC", evaluate(p, {}, [], at(OPENED))[1])

    def test_proposal_opened_after_the_pr_does_not_delay(self):
        p = pr(["kind: normative"], body="Closes #16", created="2026-10-10T00:00:00Z")
        self.assertEqual(evaluate(p, PROPOSAL, DECISION, at("2026-10-17T00:00:00Z"))[0], "success")


if __name__ == "__main__":
    unittest.main()
