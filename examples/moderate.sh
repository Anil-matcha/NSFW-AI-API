#!/usr/bin/env bash
# Usage: MUAPI_API_KEY=... ./moderate.sh "text to check" [image_url] [scene]
set -euo pipefail
TEXT="${1:?text required}"; IMAGE="${2:-}"; SCENE="${3:-social}"
BODY=$(python3 - "$TEXT" "$IMAGE" "$SCENE" <<'PY'
import json, sys
t, i, s = sys.argv[1:4]
b = {"text": t, "scene": s}
if i: b["image_url"] = i
print(json.dumps(b))
PY
)
REQ=$(curl -sS -X POST https://api.muapi.ai/api/v1/nsfw-moderation \
  -H "Content-Type: application/json" -H "x-api-key: $MUAPI_API_KEY" -d "$BODY" | python3 -c 'import sys,json;print(json.load(sys.stdin)["request_id"])')
for _ in $(seq 1 30); do
  RES=$(curl -sS "https://api.muapi.ai/api/v1/predictions/$REQ/result" -H "x-api-key: $MUAPI_API_KEY")
  STATUS=$(echo "$RES" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("status",""))')
  case "$STATUS" in completed|failed) echo "$RES"; exit 0;; esac
  sleep 1
done
echo "timed out waiting for $REQ" >&2; exit 1
