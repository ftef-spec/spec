# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Generate the Quartz content folder for the FTEF reading site from this repository.

    python docs-site/build_content.py --repo . --out docs-site/.build/content

Nothing here is written by hand into the content: the specification of every release tag, the unreleased main text,
the decision records and the review periods are read from git and the repository files at build time. The glossary
is built from section 3 (Terms and definitions) of the newest release, with the places each term is used.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

GITHUB = "https://github.com/ftef-spec/spec"
SITE = "https://ftef.vdhome.be"
DISCUSSIONS = f"{GITHUB}/discussions"
ADVISORY = f"{GITHUB}/security/advisories/new"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


def releases(repo: Path) -> dict[str, str]:
    """MAJOR.MINOR -> the newest v* tag of that line, in version order."""
    out: dict[str, str] = {}
    for tag in git(repo, "tag", "-l", "v*", "--sort=v:refname").split():
        m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag)
        if m:
            out[f"{m[1]}.{m[2]}"] = tag
    return out


def tag_date(repo: Path, tag: str) -> str:
    return git(repo, "log", "-1", "--format=%cs", tag).strip()


def slug(text: str) -> str:
    """Heading ids as Quartz makes them (github-slugger): lower case, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[`*_]", "", text.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


SOURCE_DATE = ""                                        # set in main(): the date of the commit being built


def front(title: str, description: str, **extra: str) -> str:
    """Frontmatter. Pages without their own date carry the date of the commit, never the date of the build."""
    extra = {"created": SOURCE_DATE, "modified": SOURCE_DATE, **extra}
    lines = ["---", f"title: {json.dumps(title)}", f"description: {json.dumps(description)}"]
    lines += [f"{k}: {v}" for k, v in extra.items()]
    return "\n".join([*lines, "---", ""])


def relink(text: str, ref: str) -> str:
    """Relative links into the repository point at the file on GitHub at that ref."""
    def fix(m: re.Match) -> str:
        label, target = m[1], m[2]
        if re.match(r"^(https?:|mailto:|#)", target):
            return m[0]
        target = target.removeprefix("../").removeprefix("./")
        return f"[{label}]({GITHUB}/blob/{ref}/{target})"
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", fix, text)


def drop_title(text: str) -> str:
    """The page title comes from the frontmatter; drop the document's own first-level heading."""
    return re.sub(r"\A# [^\n]*\n", "", text, count=1)


def spec_pages(repo: Path, out: Path, rel: dict[str, str]) -> None:
    for line, tag in rel.items():
        text = git(repo, "show", f"{tag}:spec/ftef.md")
        banner = (f"> [!info] Release {tag}, tagged {tag_date(repo, tag)}\n"
                  f"> This page renders `spec/ftef.md` at tag [{tag}]({GITHUB}/tree/{tag}). The file in the repository "
                  f"at that tag is the normative text. FTEF is a pre-draft: see [[review|How to review]].\n\n")
        (out / "spec").mkdir(parents=True, exist_ok=True)
        (out / "spec" / f"{line}.md").write_text(
            front(f"FTEF {line} specification", f"The FTEF {line} specification as released in {tag}.",
                  aliases=f'["spec/{line}/index"]', created=tag_date(repo, tag), modified=tag_date(repo, tag))
            + banner + relink(drop_title(text), tag), encoding="utf-8", newline="\n")
    head = git(repo, "rev-parse", "HEAD").strip()
    text = (repo / "spec" / "ftef.md").read_text(encoding="utf-8")
    banner = (f"> [!warning] Unreleased: may change at any time\n"
              f"> This is `spec/ftef.md` on the main branch at [{head[:7]}]({GITHUB}/tree/{head}). It includes merged "
              f"proposals that no release carries yet. Cite a release, not this page.\n\n")
    when = git(repo, "log", "-1", "--format=%cs", "--", "spec/ftef.md").strip()
    (out / "spec" / "main.md").write_text(
        front("FTEF specification, unreleased main", "The FTEF specification on the main branch: unreleased.",
              aliases='["spec/main/index"]', created=when, modified=when)
        + banner + relink(drop_title(text), head), encoding="utf-8", newline="\n")
    newest = list(rel)[-1]
    (out / "spec" / "index.md").write_text(
        front("Specification", "Every release of the FTEF specification, and the unreleased main text.")
        + "Each release of the specification, newest first, and the main branch. Cite a release: "
        + f"[[spec/{newest}|FTEF {newest}]] is the newest. Main carries merged changes that no release has yet.\n",
        encoding="utf-8", newline="\n")


def decision_pages(repo: Path, out: Path) -> None:
    d = out / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    for f in sorted((repo / "decisions").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"# (\S+): (.*)", text)
        num, title = (m[1], m[2]) if m else (f.stem[:4], f.stem)
        status = re.search(r"^- Status: (.*)$", text, re.M)
        when = git(repo, "log", "-1", "--format=%cs", "--", f"decisions/{f.name}").strip()
        (d / f.name).write_text(
            front(f"{num}: {title}", f"FTEF decision record {num}: {title}." + (f" Status: {status[1]}." if status else ""),
                  created=when, modified=when)
            + f"> [!info] Decision record `decisions/{f.name}` on main. [Source]({GITHUB}/blob/main/decisions/{f.name})\n\n"
            + relink(drop_title(text), "main"), encoding="utf-8", newline="\n")
    (d / "index.md").write_text(
        front("Decision records", "Why FTEF is the way it is: every normative change lands with a record.")
        + "Every normative change lands with a decision record (`CONTRIBUTING.md`). The records on the main branch:\n",
        encoding="utf-8", newline="\n")


def glossary_pages(repo: Path, out: Path, rel: dict[str, str]) -> None:
    line, tag = list(rel.items())[-1]
    text = git(repo, "show", f"{tag}:spec/ftef.md")
    sec3 = re.search(r"^## 3 Terms and definitions\n(.*?)^## ", text, re.M | re.S)[1]
    terms = re.findall(r"^- \*\*(.+?):\*\* (.+)$", sec3, re.M)
    sections = re.split(r"(?m)^(#{2,4} .+)$", text)
    d = out / "glossary"
    d.mkdir(parents=True, exist_ok=True)
    index = [front("Glossary", f"The terms defined in section 3 of FTEF {line}, and where each is used."),
             f"The terms of section 3 of the [[spec/{line}|FTEF {line} specification]] ({tag}). Each page says "
             f"where the term is used."]
    for term, definition in terms:
        pat = re.compile(r"\b" + re.escape(term.lower()) + r"(s|es)?\b")
        used = []
        for i in range(1, len(sections) - 1, 2):
            heading, body = sections[i], sections[i + 1]
            title = heading.lstrip("#").strip()
            if title.startswith("3 Terms"):
                continue
            n = len(pat.findall(body.lower()))
            if n:
                used.append(f"- [[spec/{line}#{slug(title)}|{title}]] ({n})")
        name = slug(term)
        (d / f"{name}.md").write_text(
            front(term, definition, created=tag_date(repo, tag), modified=tag_date(repo, tag))
            + f"**{term}:** {definition}\n\n"
            + f"Defined in section 3 of [[spec/{line}#3-terms-and-definitions|FTEF {line}]].\n\n"
            + "## Used in\n\n" + ("\n".join(used) if used else "- (not used elsewhere in the text)") + "\n",
            encoding="utf-8", newline="\n")
    (d / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")


def review_page(repo: Path, out: Path) -> None:
    contrib = (repo / "CONTRIBUTING.md").read_text(encoding="utf-8")
    table = re.search(r"^\| Kind \|.*?(?=\n\n)", contrib, re.M | re.S)[0]
    clock = re.search(r"^A review period runs from.*?(?=\n\n)", contrib, re.M | re.S)
    (out / "review.md").write_text(front("How to review", "How to read, question and challenge FTEF.") + f"""
> [!warning] What this is
> FTEF is a **pre-draft** with **one author**. Most of its text was drafted with an AI assistant and reviewed and
> signed off by the maintainer. Nobody else has implemented it yet. It needs critical review more than anything else.

## What helps most
- **Disagree in public.** If a rule is wrong, unclear, unworkable or already solved elsewhere, say so in
  [Discussions]({DISCUSSIONS}) or in an issue. Pointing at prior art FTEF should reuse is as useful as a new idea.
- **Propose a change** as an issue titled "Proposal: ...". It stays open for review before anything lands.
- **Try it.** Run the [reference evaluator and checker]({GITHUB}/tree/main/tools) on your own records and the
  [examples]({GITHUB}/tree/main/examples), and tell us where it breaks.
- **Report security flaws privately.** A flaw that lets a partner obtain more trust than its evidence supports is a
  security issue: use [private vulnerability reporting]({ADVISORY}), never a public issue.

## Review periods
From `CONTRIBUTING.md` on main:

{table}
{chr(10) + clock[0] + chr(10) if clock else ''}
## Where to start reading
- [[spec/index|The specification]]: the newest release, or main for what has merged since.
- [[glossary/index|The glossary]]: the terms, and where each is used.
- [[decisions/index|The decision records]]: why each rule is there.
- [[roadmap|The roadmap]]: what is planned and what is frozen.
""", encoding="utf-8", newline="\n")


def roadmap_page(out: Path) -> None:
    (out / "roadmap.md").write_text(front("Roadmap", "Where FTEF is going: the roadmap issues and milestones.") + f"""
The roadmaps live in the issue tracker, so they never go stale here:

- [Roadmap to 0.2.0, issue #19]({GITHUB}/issues/19) and its [milestone]({GITHUB}/milestone/1).
- [Roadmap to 0.3.0, issue #45]({GITHUB}/issues/45) and its [milestone]({GITHUB}/milestone/2).
- [Open proposals]({GITHUB}/issues?q=is%3Aissue+is%3Aopen+label%3Aproposal).
""", encoding="utf-8", newline="\n")


def index_page(repo: Path, out: Path, rel: dict[str, str]) -> None:
    readme = (repo / "README.md").read_text(encoding="utf-8")
    tagline = re.search(r"^\*(.+)\*$", readme, re.M)
    line, tag = list(rel.items())[-1]
    schemas = []
    for ln, t in rel.items():
        for f in git(repo, "ls-tree", "--name-only", f"{t}:schemas/{ln}").split():
            schemas.append(f"- [`schema/{ln}/{f}`]({SITE}/schema/{ln}/{f}) ({t})")
    (out / "index.md").write_text(front("FTEF", "Federated Trust Evidence Framework: an open specification for trust "
                                               "between domains, earned by evidence.") + f"""
**Federated Trust Evidence Framework.** {tagline[1] if tagline else ''}

> [!warning] Pre-draft
> FTEF is a pre-draft with one author and no outside implementation yet. Anything may change. Critical review is the
> most useful contribution: see [[review|How to review]].

- [[spec/{line}|Read the specification]] (release {tag}), or [[spec/index|every version]].
- [[glossary/index|Glossary]] and [[decisions/index|decision records]].
- [[roadmap|Roadmap]] and [[review|how to review]].
- Source, issues and discussions: [github.com/ftef-spec/spec]({GITHUB}).

## Schemas and identifiers
The schemas are served from release tags only, at their `$id` paths; the files of a released version never change
(section 7.4).

{chr(10).join(schemas)}

Trust mark type for profile 8.1: [`trust-mark/{line}/partner-evidence`]({SITE}/trust-mark/{line}/partner-evidence/).
""", encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    repo, out = a.repo.resolve(), a.out
    global SOURCE_DATE
    SOURCE_DATE = git(repo, "log", "-1", "--format=%cs").strip()
    rel = releases(repo)
    if not rel:
        raise SystemExit("no release tag v*: the reading site renders released specifications; fetch tags first")
    out.mkdir(parents=True, exist_ok=True)
    spec_pages(repo, out, rel)
    decision_pages(repo, out)
    glossary_pages(repo, out, rel)
    review_page(repo, out)
    roadmap_page(out)
    index_page(repo, out, rel)
    print(f"content for {', '.join(rel)} written to {out}")


if __name__ == "__main__":
    main()
