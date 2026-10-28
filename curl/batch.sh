#!/usr/bin/env bash
#
# SchoolDigger async batch API with curl: submit, poll, download, (cancel)
#
# POST https://api.schooldigger.com/batches runs up to 2,000 API GET calls for you,
# paced at half your plan's per-minute limit. Results come back in parts of 20 as
# gzipped NDJSON. Each item counts as one API call; submitting, polling and
# downloading are free. Paid plans only (Developer/DEMO keys get 403).
#
# Prerequisites:
#   export SCHOOLDIGGER_APP_ID=your_app_id
#   export SCHOOLDIGGER_APP_KEY=your_app_key
#   python (only to pick fields out of the JSON)
#
# Guide: https://developer.schooldigger.com/batch-requests-schooldigger-api

set -euo pipefail

BASE="https://api.schooldigger.com"
AUTH="appID=${SCHOOLDIGGER_APP_ID}&appKey=${SCHOOLDIGGER_APP_KEY}"
field() { python -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }

# ── 1. Submit ──────────────────────────────────────────────────────────────
# Each item: your own id (optional, 1-64 chars) and an API path without appID/appKey.
# The response is 202 with batchId, partCount and statusUrl.
echo "=== 1. Submit a 3-item batch ==="
SUBMIT=$(curl -s -X POST "${BASE}/batches?${AUTH}" \
  -H "Content-Type: application/json" \
  -d '{"items":[
        {"id":"lfp",     "path":"/v3.1/schools/530792001309"},
        {"id":"cascade", "path":"/v3.1/schools/530792003116"},
        {"id":"search",  "path":"/v3.1/schools?st=WA&q=Lincoln&perPage=5"}
      ]}')
echo "$SUBMIT" | python -m json.tool
BATCH_ID=$(echo "$SUBMIT" | field batchId)
echo

# ── 2. Poll status ─────────────────────────────────────────────────────────
# While queued or running, the Retry-After header says how long to wait.
# partsReady lists the parts you can download now.
echo "=== 2. Poll ${BATCH_ID} until it finishes ==="
while true; do
  HEADERS=$(mktemp)
  STATUS=$(curl -s -D "$HEADERS" "${BASE}/batches/${BATCH_ID}?${AUTH}")
  STATE=$(echo "$STATUS" | field status)
  echo "  status: ${STATE}"
  if [ "$STATE" != "queued" ] && [ "$STATE" != "running" ]; then rm -f "$HEADERS"; break; fi
  WAIT=$(grep -i '^retry-after:' "$HEADERS" | tr -dc '0-9'); rm -f "$HEADERS"
  sleep "${WAIT:-15}"
done
echo "$STATUS" | python -m json.tool
echo

# ── 3. Download results ────────────────────────────────────────────────────
# One part per call (part=0 .. partCount-1), gzipped NDJSON: --compressed unzips it.
# Each line: {"id","path","status","body"}; body is exactly what the GET returns.
# 409 = part not ready yet; 410 = deleted after the 72-hour retention.
echo "=== 3. Download part 0 (one line per item) ==="
curl -s --compressed "${BASE}/batches/${BATCH_ID}/results?part=0&${AUTH}" \
  | python -c "import json,sys; [print(r['id'], r['status'], (r['body'] or {}).get('schoolName') or (r['body'] or {}).get('numberOfSchools')) for r in map(json.loads, sys.stdin)]"
echo

# ── Cancel ─────────────────────────────────────────────────────────────────
# DELETE stops a queued or running batch and returns its status (an ended batch
# is returned unchanged). Calls already made still count.
echo "=== Cancel (no-op here: the batch has already ended) ==="
curl -s -X DELETE "${BASE}/batches/${BATCH_ID}?${AUTH}" | python -c "import json,sys; print(json.load(sys.stdin)['status'])"
