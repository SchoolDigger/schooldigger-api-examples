"""
Export school rankings to a CSV file using the SchoolDigger API.

Paginates through a state's school ranking list and writes the results
to a CSV file with key metrics for each school.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python export_rankings_csv.py [state] [level]

    state: Two-letter state code (default: WA)
    level: Elementary, Middle, or High (default: Elementary)

Output: {state}_{level}_rankings.csv
"""

import csv
import os
import sys
import requests


API_BASE = "https://api.schooldigger.com/v2.3"
PER_PAGE = 50


def get_credentials() -> tuple[str, str]:
    """Read API credentials from environment variables."""
    app_id = os.environ.get("SCHOOLDIGGER_APP_ID")
    app_key = os.environ.get("SCHOOLDIGGER_APP_KEY")
    if not app_id or not app_key:
        print("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.")
        print("Get a free API key at https://developer.schooldigger.com")
        sys.exit(1)
    return app_id, app_key


def fetch_rankings_page(
    state: str,
    level: str,
    page: int,
    app_id: str,
    app_key: str,
) -> dict:
    """Fetch one page of school rankings."""
    url = f"{API_BASE}/rankings/schools/{state}"
    params = {
        "level": level,
        "page": page,
        "perPage": PER_PAGE,
        "appID": app_id,
        "appKey": app_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def export_rankings(state: str, level: str, app_id: str, app_key: str) -> str:
    """Fetch all ranking pages and write to CSV. Returns the output filename."""
    filename = f"{state}_{level}_rankings.csv"

    # Fetch first page to get total count
    print(f"Fetching {level} school rankings for {state}...")
    data = fetch_rankings_page(state, level, 1, app_id, app_key)
    total_schools = data.get("numberOfSchools", 0)
    # SchoolDigger year convention: year 2025 = 2024-25 school year
    rank_year = data.get("rankYear", "")
    total_pages = (total_schools + PER_PAGE - 1) // PER_PAGE

    print(f"  Rank year: {rank_year - 1}-{str(rank_year)[2:]}" if rank_year else "")
    print(f"  Total schools: {total_schools}")
    print(f"  Pages to fetch: {total_pages}")

    all_schools: list[dict] = data.get("schoolList", [])

    # Fetch remaining pages
    for page in range(2, total_pages + 1):
        print(f"  Fetching page {page}/{total_pages}...")
        page_data = fetch_rankings_page(state, level, page, app_id, app_key)
        all_schools.extend(page_data.get("schoolList", []))

    # Write CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank",
            "School Name",
            "City",
            "District",
            "Stars",
            "Statewide Percentile %",
            "Students",
            "Free/Reduced Lunch %",
        ])

        for school in all_schools:
            rank_history = school.get("rankHistory", [])
            rank = rank_history[0].get("rank", "") if rank_history else ""
            stars = rank_history[0].get("rankStars", "") if rank_history else ""

            yearly = school.get("schoolYearlyDetails", [])
            latest = yearly[0] if yearly else {}

            # Average standard score from rank history if available
            avg_score = rank_history[0].get("rankStatewidePercentage", "") if rank_history else ""

            writer.writerow([
                rank,
                school.get("schoolName", ""),
                school.get("address", {}).get("city", ""),
                school.get("district", {}).get("districtName", ""),
                stars,
                avg_score,
                latest.get("numberOfStudents", ""),
                latest.get("percentFreeDiscLunch", ""),
            ])

    print(f"\nExported {len(all_schools)} schools to {filename}")
    return filename


def main() -> None:
    app_id, app_key = get_credentials()

    state = sys.argv[1].upper() if len(sys.argv) > 1 else "WA"
    level = sys.argv[2].capitalize() if len(sys.argv) > 2 else "Elementary"

    if level not in ("Elementary", "Middle", "High"):
        print(f"Error: Level must be Elementary, Middle, or High (got '{level}')")
        sys.exit(1)

    try:
        export_rankings(state, level, app_id, app_key)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
