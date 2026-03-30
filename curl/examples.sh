#!/usr/bin/env bash
#
# SchoolDigger API — curl examples for every endpoint
#
# Prerequisites:
#   export SCHOOLDIGGER_APP_ID=your_app_id
#   export SCHOOLDIGGER_APP_KEY=your_app_key
#
# Get a free API key at https://developer.schooldigger.com
# Output is piped through `python -m json.tool` for pretty printing.
#
# Plan levels referenced below:
#   Free  — DEV/TEST tier, 20 calls/day, no credit card
#   Paid  — $19.90/mo+, higher call limits
#   Pro   — $89/mo+, unlocks location search and boundary data
#   Enterprise — $189/mo+, full access

set -euo pipefail

BASE="https://api.schooldigger.com/v2.3"
AUTH="appID=${SCHOOLDIGGER_APP_ID}&appKey=${SCHOOLDIGGER_APP_KEY}"


# ── 1. Search schools ────────────────────────────────────────────────────────
# Find schools in a state matching a name keyword.
# Supports: st (state), q (keyword), city, zip, level, type, page, perPage
# Plan: Free

echo "=== 1. Search schools (WA, keyword: Lincoln) ==="
curl -s "${BASE}/schools?st=WA&q=Lincoln&${AUTH}" | python -m json.tool
echo


# ── 2. Get school detail ─────────────────────────────────────────────────────
# Full school record: test scores, rankings, demographics, finance, reviews.
# Default school: 530792001309 = Lake Forest Park Elementary, WA
# Plan: Free (test scores, finance, reviews require Paid+)

echo "=== 2. Get school detail (Lake Forest Park Elementary) ==="
curl -s "${BASE}/schools/530792001309?${AUTH}" | python -m json.tool
echo


# ── 3. Search districts ──────────────────────────────────────────────────────
# Find school districts by state and keyword.
# Plan: Free

echo "=== 3. Search districts (WA, keyword: Shoreline) ==="
curl -s "${BASE}/districts?st=WA&q=Shoreline&${AUTH}" | python -m json.tool
echo


# ── 4. Get district detail ───────────────────────────────────────────────────
# Full district record including test scores, finance, and boundary data.
# District ID: 5307920 = Shoreline School District, WA
# Boundary polygons require Pro or Enterprise plan.
# Plan: Free (boundaries require Pro+)

echo "=== 4. Get district detail (Shoreline School District) ==="
curl -s "${BASE}/districts/5307920?${AUTH}" | python -m json.tool
echo


# ── 5. School rankings ───────────────────────────────────────────────────────
# Statewide ranked list of schools for a given level.
# level: Elementary | Middle | High
# SchoolDigger year convention: rankYear 2025 = 2024-25 school year
# Plan: Free

echo "=== 5. School rankings (WA Elementary, page 1 of 10 per page) ==="
curl -s "${BASE}/rankings/schools/WA?level=Elementary&page=1&perPage=10&${AUTH}" | python -m json.tool
echo


# ── 6. District rankings ─────────────────────────────────────────────────────
# Statewide ranked list of districts.
# Plan: Free

echo "=== 6. District rankings (WA, page 1 of 10 per page) ==="
curl -s "${BASE}/rankings/districts/WA?page=1&perPage=10&${AUTH}" | python -m json.tool
echo


# ── 7. Autocomplete schools ──────────────────────────────────────────────────
# Fast typeahead search — call on each keystroke (debounced) to power
# instant search UIs. Returns school IDs you can pass to endpoint #2.
# Plan: Free

echo "=== 7. Autocomplete schools (query: 'Linco', state: WA) ==="
curl -s "${BASE}/autocomplete/schools?q=Linco&st=WA&${AUTH}" | python -m json.tool
echo


# ── 8. Autocomplete districts ────────────────────────────────────────────────
# Same typeahead pattern for district search.
# Plan: Free

echo "=== 8. Autocomplete districts (query: 'Shore', state: WA) ==="
curl -s "${BASE}/autocomplete/districts?q=Shore&st=WA&${AUTH}" | python -m json.tool
echo


# ── Bonus: Location-based school search ──────────────────────────────────────
# Find schools near a lat/lon within a radius.
# Default coordinates: Lake Forest Park, WA (47.7631, -122.2878)
# Plan: Pro or Enterprise required

echo "=== Bonus: Nearby schools (Lake Forest Park, WA — requires Pro/Enterprise) ==="
curl -s "${BASE}/schools?st=WA&nearLatitude=47.7631&nearLongitude=-122.2878&distanceMiles=3&${AUTH}" | python -m json.tool
echo
