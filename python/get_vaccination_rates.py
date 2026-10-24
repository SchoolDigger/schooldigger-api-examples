"""
Fetch and display a school's vaccination rates from the SchoolDigger API (v3.1).

API 3.1 adds a `vaccination` object to /schools/{id}: the rates the state
published for the school (source, headline figure, and every figure by year,
grade, vaccine and status, with the state's own district, county and state
figures). It is absent when the school's state publishes no vaccination data.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python get_vaccination_rates.py [school_id]

    Default school ID: 530111000200 (Progress Elementary, WA)
"""

import os
import sys
import requests


API_BASE = "https://api.schooldigger.com/v3.1"


def get_credentials() -> tuple[str, str]:
    """Read API credentials from environment variables."""
    app_id = os.environ.get("SCHOOLDIGGER_APP_ID")
    app_key = os.environ.get("SCHOOLDIGGER_APP_KEY")
    if not app_id or not app_key:
        print("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.")
        print("Get a free API key at https://developer.schooldigger.com")
        sys.exit(1)
    return app_id, app_key


def get_school(school_id: str, app_id: str, app_key: str) -> dict:
    """Fetch a school with every vaccination figure (includeVaccinationDetail=true)."""
    url = f"{API_BASE}/schools/{school_id}"
    params = {"appID": app_id, "appKey": app_key, "includeVaccinationDetail": "true"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def year_label(year) -> str:
    # SchoolDigger year convention: year 2026 = 2025-26 school year
    return f"{year - 1}-{str(year)[2:]}" if year else "N/A"


def format_value(value) -> str:
    """Render a vaccination value as the state published it."""
    if not value:
        return "N/A"
    status = value.get("status")
    if status == "exact":
        return f"{value['pct']:.1f}%"
    if status == "range":
        return f"{value['rangeLow']:g}-{value['rangeHigh']:g}%"
    return status  # suppressed, redactedCount, countOnly or invalid


def display_vaccination(school: dict) -> None:
    """Display the headline and the latest year's school, district, county and state figures."""
    print(f"\n{'=' * 60}")
    print(f"  {school.get('schoolName', 'N/A')} — vaccination rates")
    print(f"{'=' * 60}")

    vax = school.get("vaccination")
    if not vax:
        print("  The school's state publishes no vaccination data.")
        return

    source = vax.get("source", {})
    print(f"  Source:   {source.get('agency', 'N/A')}")
    print(f"            {source.get('url', '')}")

    headline = vax.get("headline")
    if headline:
        print(f"\n  {headline.get('label', 'Headline')} ({year_label(headline.get('year'))}):"
              f" {format_value(headline.get('value'))}")
        if headline.get("exemptionRate") is not None:
            print(f"  Exemption rate: {headline['exemptionRate']:.1f}%")

    # Figures come most recent year first; show the headline grade and vaccine across statuses
    figures = vax.get("figures", [])
    if not figures:
        return
    latest = figures[0]["year"]
    grade = headline.get("grade") if headline else figures[0]["grade"]
    antigen = headline.get("antigen", {}).get("code") if headline else figures[0]["antigen"]
    statuses = {s["code"]: s["name"] for s in vax.get("statuses", [])}

    print(f"\n--- {year_label(latest)}, grade {grade}, vaccine {antigen} ---\n")
    print(f"  {'Status':<34} {'School':>8} {'District':>9} {'County':>8} {'State':>8}")
    print(f"  {'-' * 34} {'-' * 8} {'-' * 9} {'-' * 8} {'-' * 8}")
    for f in figures:
        if f["year"] != latest or f["grade"] != grade or f["antigen"] != antigen:
            continue
        cols = [format_value(f.get(level)) for level in ("school", "district", "county", "state")]
        print(f"  {statuses.get(f['status'], f['status'])[:34]:<34} "
              f"{cols[0]:>8} {cols[1]:>9} {cols[2]:>8} {cols[3]:>8}")
    print(f"\n  District: {vax.get('districtName', 'N/A')}  County: {vax.get('countyName', 'N/A')}")
    print(f"  Years available: {', '.join(year_label(y) for y in vax.get('yearsAvailable', []))}")


def main() -> None:
    app_id, app_key = get_credentials()

    school_id = sys.argv[1] if len(sys.argv) > 1 else "530111000200"
    print(f"Fetching vaccination rates for school ID: {school_id}...")

    try:
        school = get_school(school_id, app_id, app_key)
        display_vaccination(school)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
