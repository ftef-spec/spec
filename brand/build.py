# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Build every FTEF brand SVG from one parametric master (64 x 64 grid).

    python brand/build.py            # writes brand/*.svg and the site copies
    python brand/build.py --check    # CI: fails when a generated file differs from this master

The outlined lockups (ftef-lockup*.svg) are made from the .src.svg files with the brand-cycle outline_text.py and
Inter (SIL Open Font License 1.1); the PNG and ICO files are rendered from the SVGs. See brand/BRAND.md.

The mark: two domains (semicircles, radius 22, centred on the edges of a gap of 4), two equal rungs of evidence
knocked out of them, and one amber rung that spans both domains, set off by a knocked-out halo. Knockouts are true
holes (fill-rule evenodd), never paint in the background colour, so every file works on any ground. A rung that
reaches past a half's rim cuts that half into pieces, drawn with exact arcs. No masks (favicon renderers and cairo
handle them poorly).
"""
import math
import sys
from pathlib import Path

PALETTES = {
    "light": {"navy": "#0B2545", "teal": "#129F95", "amber": "#F2A541", "ink": "#0B2545", "ink2": "#3A4A5C"},
    "dark": {"navy": "#5B8BD0", "teal": "#2CC4B8", "amber": "#F7B955", "ink": "#F5F7FA", "ink2": "#C9D3DF"},
}
TITLE = "FTEF mark: two domains joined by rungs of evidence"
MARK = {"rungs": [(22, 12), (31, 12)], "amber": (40, 20), "t": 4}     # (y, half-length); t = bar thickness
SMALL = {"rungs": [(22, 12)], "amber": (38, 20), "t": 6}             # 16-32 px: one white rung, thicker bars
R, GAP, CY, HALO = 22, 4, 32, 1.5


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def half(side, bars):
    """side -1 = left, +1 = right; bars: (y, half-length, half-thickness). An evenodd path."""
    edge = 32 + side * GAP / 2

    def xc(y):
        return edge + side * math.sqrt(max(0.0, R * R - (y - CY) ** 2))

    cuts, holes = [], []
    for y, L, h in bars:
        outer = 32 + side * L
        reach = min(abs(xc(y - h) - edge), abs(xc(y + h) - edge))
        if abs(outer - edge) - h >= reach:              # passes the rim: cuts the half into pieces
            cuts.append((y - h, y + h))
        else:
            x0 = outer - side * h                       # centre of the round end
            if side < 0:
                holes.append(f"M{f(x0)} {f(y - h)}H{f(edge)}V{f(y + h)}H{f(x0)}A{f(h)} {f(h)} 0 0 1 {f(x0)} {f(y - h)}Z")
            else:
                holes.append(f"M{f(edge)} {f(y - h)}H{f(x0)}A{f(h)} {f(h)} 0 0 1 {f(x0)} {f(y + h)}H{f(edge)}Z")
    spans, top = [], CY - R
    for a, b in sorted(cuts):
        if a > top:
            spans.append((top, a))
        top = max(top, b)
    if top < CY + R:
        spans.append((top, CY + R))
    sweep = 0 if side < 0 else 1
    d = ""
    for a, b in spans:
        xa, xb = xc(a), xc(b)
        d += f"M{f(edge)} {f(a)}" + (f"H{f(xa)}" if abs(xa - edge) > 1e-9 else "")
        d += f"A{R} {R} 0 0 {sweep} {f(xb)} {f(b)}" + (f"H{f(edge)}" if abs(xb - edge) > 1e-9 else "") + "Z"
    return d + "".join(holes)


def parts(spec):
    h = spec["t"] / 2
    ay, al = spec["amber"]
    bars = [(y, L, h) for y, L in spec["rungs"]] + [(ay, al + HALO, h + HALO)]
    amber = (f'<rect x="{f(32 - al)}" y="{f(ay - h)}" width="{f(2 * al)}" height="{f(spec["t"])}" '
             f'rx="{f(h)}"')
    return half(-1, bars), half(1, bars), amber


def mark_body(spec, pal):
    left, right, amber = parts(spec)
    p = PALETTES[pal]
    return (f'<path fill="{p["navy"]}" fill-rule="evenodd" d="{left}"/>'
            f'<path fill="{p["teal"]}" fill-rule="evenodd" d="{right}"/>{amber} fill="{p["amber"]}"/>')


def wrap(body, w=64, h=64, title=TITLE, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{title}</title>'
            f'{extra}{body}</svg>\n')


def mono(spec):
    left, right, amber = parts(spec)
    return wrap(f'<g fill="currentColor"><path fill-rule="evenodd" d="{left}{right}"/>{amber}/></g>')


def favicon():
    """Small mark; light and dark palettes by prefers-color-scheme (Chrome, Firefox; Safari uses the ICO)."""
    left, right, amber = parts(SMALL)
    lp, dp = PALETTES["light"], PALETTES["dark"]
    style = (f'<style>.n{{fill:{lp["navy"]}}}.t{{fill:{lp["teal"]}}}.a{{fill:{lp["amber"]}}}'
             f'@media (prefers-color-scheme:dark){{.n{{fill:{dp["navy"]}}}.t{{fill:{dp["teal"]}}}.a{{fill:{dp["amber"]}}}}}</style>')
    body = (f'<path class="n" fill-rule="evenodd" d="{left}"/><path class="t" fill-rule="evenodd" d="{right}"/>'
            f'{amber} class="a"/>')
    return wrap(body, extra=style)


def lockup(pal):
    """Mark plus wordmark, live text (outline it with the brand-cycle outline_text.py before shipping)."""
    p = PALETTES[pal]
    body = (f'<g transform="translate(4 4) scale(1.125)">{mark_body(MARK, pal)}</g>'
            f'<text x="92" y="44" font-family="Inter" font-weight="700" font-size="40" letter-spacing="1" '
            f'fill="{p["ink"]}">FTEF</text>'
            f'<text x="94" y="66" font-family="Inter Medium" font-size="13.5" fill="{p["ink2"]}">'
            f'Federated Trust Evidence Framework</text>')
    return wrap(body, w=344, h=80, title="FTEF: Federated Trust Evidence Framework")


def outputs():
    """Every generated file, by path relative to the repository root."""
    files = {
        "ftef-mark.svg": wrap(mark_body(MARK, "light")),
        "ftef-mark-dark.svg": wrap(mark_body(MARK, "dark")),
        "ftef-mark-mono.svg": mono(MARK),
        "ftef-mark-small.svg": wrap(mark_body(SMALL, "light")),
        "ftef-mark-small-dark.svg": wrap(mark_body(SMALL, "dark")),
        "favicon.svg": favicon(),
        "ftef-lockup.src.svg": lockup("light"),
        "ftef-lockup-dark.src.svg": lockup("dark"),
    }
    out = {f"brand/{n}": t for n, t in files.items()}
    for n in ("favicon.svg", "ftef-mark.svg", "ftef-mark-dark.svg"):     # the site serves its own copies
        out[f"site/{n}"] = files[n]
    return out


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    check = "--check" in sys.argv
    stale = []
    for rel, text in outputs().items():
        path = root / rel
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(rel)
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"{rel:34} {len(text.encode()):5} bytes")
    if stale:
        print("out of date with brand/build.py (run it):", ", ".join(stale))
        sys.exit(1)
    if check:
        print("brand files match brand/build.py")
