# FTEF brand

<p>
  <img src="ftef-mark.svg" width="96" alt="FTEF mark">
  <img src="ftef-mark-dark.svg" width="96" alt="FTEF mark, dark-ground colours">
  <img src="ftef-mark-small.svg" width="48" alt="FTEF mark, small sizes">
</p>

## The mark

Two domains, joined by evidence. The two halves are the relying party's domain and the partner's, separated by a
gap: neither is part of the other. The white rungs are evidence that crosses the gap. The amber rung, the longest,
spans both domains: the bounded risk acceptance, the one thing that may lift trust above what the evidence supports,
always visibly set apart (its halo).

What it must not look like: a shield, a padlock or a key (security vendors), interlocking circles or a chain
(blockchain), a cross (medical).

## Files

All SVGs come from one parametric master, [`build.py`](build.py) (64 x 64 grid). Do not edit them by hand: change the
master, run `python brand/build.py`, and CI checks the result with `python brand/build.py --check`.

| File | Use |
|---|---|
| `ftef-mark.svg` | the mark on light grounds |
| `ftef-mark-dark.svg` | the mark on dark grounds |
| `ftef-mark-mono.svg` | one colour (`currentColor`), for print, stamps and themed icons; inline only |
| `ftef-mark-small.svg`, `ftef-mark-small-dark.svg` | 16 to 32 px: one white rung, thicker bars |
| `favicon.svg` | the small mark, light and dark by `prefers-color-scheme` (Chrome, Firefox); copied to `site/` |
| `ftef-lockup.svg`, `ftef-lockup-dark.svg` | mark and wordmark, text outlined to paths (renders without the font) |
| `ftef-lockup.src.svg`, `ftef-lockup-dark.src.svg` | the lockups with live text, to re-typeset |
| `ftef-avatar.png` | 512 x 512, organisation avatar |
| `ftef-social.png` | 1280 x 640, repository social preview |
| `../site/favicon.ico`, `../site/apple-touch-icon.png` | 16/32/48 px ICO (Safari, old browsers); 180 px touch icon |

Geometry: semicircles of radius 22 centred on the edges of a gap of 4; bars 4 thick (6 in the small mark) with round
ends; the amber rung's halo is 1.5. Knockouts are real holes (`fill-rule="evenodd"`), so every file works on any
ground. Clear space around the mark: at least a quarter of its width. Smallest size: the full mark from 48 px, the
small mark below.

## Colours

| Role | Light ground | Dark ground |
|---|---|---|
| domain (left) | navy `#0B2545` | `#5B8BD0` |
| domain (right) | teal `#129F95` | `#2CC4B8` |
| risk acceptance | amber `#F2A541` | `#F7B955` |
| ink (wordmark) | `#0B2545` | `#F5F7FA` |
| secondary ink | `#3A4A5C` | `#C9D3DF` |
| paper | `#F5F7FA` | `#1B2533` |
| text in teal | `#0E7C74` | `#2CC4B8` |

Checked with the brand-cycle `palette_check.py`: both domains reach 3:1 against their ground (graphics, WCAG 1.4.11);
teal text uses `#0E7C74` (4.7:1 on paper) because the brand teal is for graphics only. Amber never carries text on a
light ground (1.9:1); it is set off from the teal by its halo, not by colour alone (amber on teal is 1.4:1).

## Typeface

[Inter](https://github.com/rsms/inter), Bold (wordmark) and Medium (name), SIL Open Font License 1.1. The shipped
lockups contain outlines, not the font. To re-typeset: edit a `.src.svg`, then outline it with the brand-cycle
`outline_text.py` and Inter 700/500 from `https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-<weight>-normal.ttf`.

## Use

The mark may be used, unmodified, to point to this project ([`TRADEMARK.md`](../TRADEMARK.md)). The files are under
the Apache License 2.0 like the rest of the code; the name rules of `TRADEMARK.md` apply on top.

## Changes

- 2026-10-22: refined from the first mark (a 512 px PNG). Rebuilt as vector from one master; two equal rungs instead
  of three tapering ones (the old layout read as a face); the amber rung spans both domains with a knocked-out halo;
  thicker bars for small sizes; teal darkened to `#129F95` for 3:1 on paper; dark-ground palette; small mark,
  favicon, lockups, avatar and social card added. Reviewed by a design and a technical reviewer.
