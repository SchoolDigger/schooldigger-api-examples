"""
Search schools using the SchoolDigger API.

Searches for schools in a given state matching a keyword and displays
results in a formatted table.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python search_schools.py
"""

import os
import sys
import requests


API_BASE = "https://api.schooldigger.com/v2.3"


def get_credentials() -> tuple[str, str]:
    """Read API credentials from environment variables."""
    app_id = os.environ.get("SCHOOLDIGGER_APP_ID")
    app_key = os.environ.get("SCHOOLDIGGER_APP_KEY")
    if not app_id or not app_key:
        print("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.")
        print("Get a free API key at https://developer.schooldigger.com")
        sys.exit(1)
    return app_id, app_key


def search_schools(state: str, query: str, app_id: str, app_key: str) -> dict:
    """Search schools by state and keyword."""
    url = f"{API_BASE}/schools"
    params = {
        "st": state,
        "q": query,
        "appID": app_id,
        "appKey": app_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def display_results(data: dict) -> None:
    """Print search results as a formatted table."""
    schools = data.get("schoolList", [])
    total = data.get("numberOfSchools", 0)

    if not schools:
        print("No schools found.")
        return

    print(f"\nFound {total} school(s). Showing first {len(schools)}:\n")

    # Table header
    header = f"{'School Name':<40} {'City':<18} {'Grades':<10} {'Rank':<14} {'Stars':<6} {'Students':<8}"
    print(header)
    print("-" * len(header))

    for school in schools:
        name = school.get("schoolName", "N/A")[:39]
        city = school.get("address", {}).get("city", "N/A")[:17]
        low = school.get("lowGrade", "?")
        high = school.get("highGrade", "?")
        grades = f"{low}-{high}"

        # Ranking info (most recent year)
        rank_history = school.get("rankHistory", [])
        if rank_history:
            r = rank_history[0]
            rank = f"{r.get('rank', '?')} of {r.get('rankOf', '?')}"
            stars = f"{r.get('rankStars', 'N/A')}"
        else:
            rank = "N/A"
            stars = "N/A"

        # Enrollment (most recent year)
        yearly = school.get("schoolYearlyDetails", [])
        students = str(yearly[0].get("numberOfStudents", "N/A")) if yearly else "N/A"

        print(f"{name:<40} {city:<18} {grades:<10} {rank:<14} {stars:<6} {students:<8}")


def main() -> None:
    app_id, app_key = get_credentials()

    state = "WA"
    query = "Lincoln"
    print(f"Searching for '{query}' schools in {state}...")

    try:
        data = search_schools(state, query, app_id, app_key)
        display_results(data)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
