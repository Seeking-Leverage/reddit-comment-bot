#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data"
EXAMPLES="$ROOT/examples"

mkdir -p "$DATA"

copy_if_missing() {
  local src="$1"
  local dest="$2"
  if [[ -f "$dest" ]]; then
    echo "skip (exists): $(basename "$dest")"
  else
    cp "$src" "$dest"
    echo "created: $(basename "$dest")"
  fi
}

copy_if_missing "$EXAMPLES/brand.example.json" "$DATA/brand.json"
copy_if_missing "$EXAMPLES/playbooks.example.json" "$DATA/playbooks.json"

if [[ ! -f "$DATA/tracker.json" ]]; then
  cat > "$DATA/tracker.json" <<'EOF'
{
  "goals": {
    "goal_upvotes": 100,
    "goal_impressions": 2000
  },
  "entries": []
}
EOF
  echo "created: tracker.json"
else
  echo "skip (exists): tracker.json"
fi

echo ""
echo "Done. Start the console with: ./scripts/dev.sh"