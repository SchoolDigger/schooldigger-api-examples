"""
Fetch and display a full school profile from the SchoolDigger API.

Retrieves detailed information for a school including demographics,
rank history, and test scores.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python get_school_detail.py [school_id]

    Default school ID: 530792001309 (Lake Forest Park Elementary, WA)
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


def get_school(school_id: str, app_id: str, app_key: str) -> dict:
    """Fetch full school detail by ID."""
    url = f"{API_BASE}/schools/{school_id}"
    params = {"appID": app_id, "appKey": app_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def display_school(school: dict) -> None:
    """Display a detailed school profile."""
    # Basic info
    name = school.get("schoolName", "N/A")
    addr = school.get("address", {})
    address_str = f"{addr.get('street', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}"
    district = school.get("district", {}).get("districtName", "N/A")
    low = school.get("lowGrade", "?")
    high = school.get("highGrade", "?")
    school_id = school.get("schoolid", "")

    yearly = school.get("schoolYearlyDetails", [])
    latest = yearly[0] if yearly else {}
    enrollment = latest.get("numberOfStudents", "N/A")
    pupil_teacher = latest.get("pupilTeacherRatio", "N/A")
    free_lunch = latest.get("percentFreeDiscLunch", "N/A")
    # SchoolDigger year convention: year 2025 = 2024-25 school year
    detail_year = latest.get("year", "")
    year_label = f"{detail_year - 1}-{str(detail_year)[2:]}" if detail_year else "N/A"

    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    print(f"  Address:    {address_str}")
    print(f"  District:   {district}")
    print(f"  Grades:     {low} – {high}")
    print(f"  Enrollment: {enrollment} ({year_label})")
    print(f"  Pupil/Teacher Ratio: {pupil_teacher}")
    if free_lunch is not None and free_lunch != "N/A":
        print(f"  Free/Reduced Lunch:  {free_lunch:.1f}%")

    # SchoolDigger URL
    print(f"\n  SchoolDigger page: https://www.schooldigger.com/go/{school_id}")

    # Demographics
    print(f"\n--- Demographics ({year_label}) ---\n")
    demo_fields = [
        ("percentWhite", "White"),
        ("percentBlack", "Black"),
        ("percentHispanic", "Hispanic"),
        ("percentAsian", "Asian"),
        ("percentAmericanIndian", "American Indian"),
        ("percentPacificIslander", "Pacific Islander"),
        ("percentTwoOrMoreRaces", "Two or More Races"),
    ]
    print(f"  {'Group':<22} {'Percent':>8}")
    print(f"  {'-' * 22} {'-' * 8}")
    for field, label in demo_fields:
        val = latest.get(field)
        if val is not None:
            print(f"  {label:<22} {val:>7.1f}%")

    # Rank history (last 5 years)
    rank_history = school.get("rankHistory", [])
    if rank_history:
        print(f"\n--- Rank History (last {min(5, len(rank_history))} years) ---\n")
        print(f"  {'Year':<12} {'Rank':<16} {'Stars':<6}")
        print(f"  {'-' * 12} {'-' * 16} {'-' * 6}")
        for r in rank_history[:5]:
            # rankStars is on a 0-5 scale
            yr = r.get("year", "")
            yr_label = f"{yr - 1}-{str(yr)[2:]}" if yr else "N/A"
            rank_str = f"{r.get('rank', '?')} of {r.get('rankOf', '?')}"
            stars = r.get("rankStars", "N/A")
            print(f"  {yr_label:<12} {rank_str:<16} {stars:<6}")

    # Test scores
    test_scores = school.get("testScores", [])
    if test_scores:
        print(f"\n--- Test Scores (most recent) ---\n")
        print(f"  {'Subject':<14} {'Grade':<8} {'Year':<10} {'% Met Standard':>15}")
        print(f"  {'-' * 14} {'-' * 8} {'-' * 10} {'-' * 15}")
        shown = set()
        for ts in test_scores:
            subject = ts.get("subject", "N/A")
            grade = ts.get("grade", "All")
            year = ts.get("year", "")
            school_score = ts.get("schoolTestScore", {})
            pct = school_score.get("percentMetStandard")
            key = (subject, grade)
            if key in shown:
                continue
            shown.add(key)
            yr_label = f"{year - 1}-{str(year)[2:]}" if year else "N/A"
            pct_str = f"{pct:.1f}%" if pct is not None else "N/A"
            print(f"  {subject:<14} {str(grade):<8} {yr_label:<10} {pct_str:>15}")
            if len(shown) >= 10:
                break
    else:
        print("\n  No test score data available.")


def main() -> None:
    app_id, app_key = get_credentials()

    school_id = sys.argv[1] if len(sys.argv) > 1 else "530792001309"
    print(f"Fetching school detail for ID: {school_id}...")

    try:
        school = get_school(school_id, app_id, app_key)
        display_school(school)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
