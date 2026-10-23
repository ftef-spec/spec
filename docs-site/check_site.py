# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Check a built FTEF reading site: every internal link and anchor resolves, and no page loads anything from
another host at runtime (scripts, styles, fonts, images, preconnects).

    python docs-site/check_site.py _site
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlparse

SELF = "ftef.vdhome.be"
LOADS = {("script", "src"), ("img", "src"), ("iframe", "src"), ("source", "srcset")}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.loads: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            rel = (a.get("rel") or "").lower()
            if any(r in rel for r in ("stylesheet", "preconnect", "preload", "icon", "modulepreload", "dns-prefetch")):
                self.loads.append(a["href"])
        for t, attr in LOADS:
            if tag == t and a.get(attr):
                self.loads.append(a[attr].split()[0])


def target(root: Path, page: Path, href: str) -> tuple[Path | None, str]:
    base = "https://" + SELF + "/" + page.relative_to(root).as_posix()
    url, frag = urldefrag(urljoin(base, href))
    u = urlparse(url)
    if u.netloc != SELF:
        return None, ""
    p = root / unquote(u.path.lstrip("/"))
    for cand in (p, p.with_name(p.name + ".html"), p / "index.html"):
        if cand.is_file():
            return cand, frag
    return p, frag


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    pages = {p: Page() for p in root.rglob("*.html")}
    for p, parser in pages.items():
        parser.feed(p.read_text(encoding="utf-8"))
    bad = []
    for p, parser in pages.items():
        rel = p.relative_to(root).as_posix()
        for src in parser.loads:
            host = urlparse(src).netloc
            if host and host != SELF:
                bad.append(f"{rel}: loads from another host: {src}")
        for href in parser.links:
            if href.startswith(("mailto:", "javascript:")):
                continue
            t, frag = target(root, p, href)
            if t is None:
                continue
            if not t.is_file():
                if re.match(r"^/?(schema|trust-mark)/", urlparse(urljoin("/", href)).path.lstrip("/")) or \
                        "/schema/" in href or "/trust-mark/" in href:
                    continue                    # added by the pages workflow after the build
                bad.append(f"{rel}: broken link {href}")
            elif frag and t.suffix == ".html" and frag not in pages.get(t, Page()).ids:
                bad.append(f"{rel}: missing anchor {href}")
    for b in bad:
        print("FAIL", b)
    print(f"{len(pages)} pages, {sum(len(x.links) for x in pages.values())} links checked, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
