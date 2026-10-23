#!/bin/sh
# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
#
# Build the FTEF reading site with a pinned Quartz into the given output directory (default: _site).
#   sh docs-site/build.sh [OUT]
# Needs git, Node 22 with npm, and Python 3. The pages workflow runs this before it adds the schemas.
set -eu

QUARTZ_REPO=https://github.com/jackyzha0/quartz.git
QUARTZ_TAG=v4.5.2
QUARTZ_SHA=4923affa7722dfc751f1074348e6dad214fe0c08

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
WORK="$HERE/.build"
OUT=${1:-$ROOT/_site}
case "$OUT" in /*|[A-Za-z]:*) ;; *) OUT="$ROOT/$OUT" ;; esac
PY=${PYTHON:-python3}

rm -rf "$WORK"
mkdir -p "$WORK"
git clone --quiet --depth 1 --branch "$QUARTZ_TAG" "$QUARTZ_REPO" "$WORK/quartz"
got=$(git -C "$WORK/quartz" rev-parse HEAD)
if [ "$got" != "$QUARTZ_SHA" ]; then
  echo "Quartz $QUARTZ_TAG resolves to $got, expected $QUARTZ_SHA: refusing to build with an unpinned Quartz"
  exit 1
fi
for p in "$HERE"/patches/*.patch; do
  git -C "$WORK/quartz" apply "$p"
done
cp "$HERE/quartz.config.ts" "$HERE/quartz.layout.ts" "$WORK/quartz/"
cp "$HERE/custom.scss" "$WORK/quartz/quartz/styles/custom.scss"
cp "$ROOT/brand/ftef-avatar.png" "$WORK/quartz/quartz/static/icon.png"
rm -rf "$WORK/quartz/quartz/static/giscus"   # comment themes we never use
cp "$ROOT/brand/ftef-social.png" "$WORK/quartz/quartz/static/og-image.png"

"$PY" "$HERE/build_content.py" --repo "$ROOT" --out "$WORK/content"

cd "$WORK/quartz"
npm ci --no-audit --no-fund
npx quartz build --directory "$WORK/content" --output "$OUT"
