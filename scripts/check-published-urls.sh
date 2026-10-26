#!/usr/bin/env bash
# Check every openagrinet.github.io URL the packs publish.
#
# Two things go wrong independently, so both are checked:
#   1. the URL does not resolve on the published site
#   2. the URL resolves but its #/components/schemas/... fragment names nothing
#
# Run from the repository root. Exits non-zero if anything fails.

set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
FILES=$(find api-schemas -type f \( -name '*.yaml' -o -name '*.json' -o -name '*.jsonld' \) \
        ! -name '*postman*')

# ---------------------------------------------------- fragments, checked locally
# A schema pointer naming a component that does not exist is wrong whether or not
# the site is up, so this half needs no network and should never be skipped.
echo "Schema pointers"
found=0
for f in $FILES; do
  while read -r pointer; do
    [ -z "$pointer" ] && continue
    found=1
    pack=$(printf '%s' "$pointer" | sed -E 's#.*/api-schemas/([^/]+)/.*#\1#')
    name=${pointer##*/}
    if grep -q "^    ${name}:$" "api-schemas/${pack}/v0.1/attributes.yaml" 2>/dev/null; then
      printf '  ok    %-26s in %s\n' "$name" "${f#api-schemas/}"
    else
      printf '  BAD   %-26s names no component in %s (from %s)\n' "$name" "$pack" "$f"
      fail=1
    fi
  done < <(grep -o 'https://openagrinet\.github\.io/network-specs/api-schemas/[A-Za-z0-9/.]*#/components/schemas/[A-Za-z]*' "$f" | sort -u)
done
[ "$found" -eq 0 ] && echo "  (none found)"

# ------------------------------------------------------------ URLs, over the wire
# `pattern:` lines hold regexes, not URLs — their backslash escapes are not part of
# any address, so they are skipped rather than de-escaped.
echo
echo "Published URLs"
urls=$(grep -h -v 'pattern:' $FILES \
       | grep -ohE 'https://openagrinet\.github\.io/network-specs[A-Za-z0-9/._#-]*' \
       | sed 's/#.*//' | sed 's#/$##' | sort -u)

for url in $urls; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -L "$url" 2>/dev/null)
  printf '  %-4s %s\n' "${code:-ERR}" "$url"
  [ "$code" = "200" ] || fail=1
done

echo
if [ "$fail" -eq 0 ]; then
  echo "All published URLs resolve and all schema pointers name real components."
else
  echo "FAILED — see the lines marked BAD or with a non-200 code above."
  echo "Note: /api-schemas/ goes live only once this branch merges into the Pages"
  echo "source branch, so a sweep of 404s there is expected until then."
fi
exit "$fail"
