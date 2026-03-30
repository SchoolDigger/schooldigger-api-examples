"""
Compare two schools side-by-side using the SchoolDigger API.

Fetches detailed profiles for two schools and displays a comparison
of key metrics including rankings, demographics, and test scores.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python compare_schools.py [school_id_1] [school_id_2]

    Defaults:
        School 1: 530792001309 (Lake Forest Park Elementary)
        School 2: 530792003116 (Cascade K-8)
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


def fmt(value, suffix: str = "", decimals: int = 1) -> str:
    """Format a value for display, returning 'N/A' if None."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.{decimals}f}{suffix}"
    return f"{value}{suffix}"


def display_comparison(s1: dict, s2: dict) -> None:
    """Display a side-by-side comparison of two schools."""
    col_w = 30

    def row(label: str, v1: str, v2: str) -> None:
        print(f"  {label:<24} {v1:<{col_w}} {v2:<{col_w}}")

    def get_latest(school: dict) -> dict:
        yearly = school.get("schoolYearlyDetails", [])
        return yearly[0] if yearly else {}

    def get_rank(school: dict) -> dict:
        history = school.get("rankHistory", [])
        return history[0] if history else {}

    l1 = get_latest(s1)
    l2 = get_latest(s2)
    r1 = get_rank(s1)
    r2 = get_rank(s2)

    name1 = s1.get("schoolName", "School 1")
    name2 = s2.get("schoolName", "School 2")

    print(f"\n{'=' * 86}")
    print(f"  School Comparison")
    print(f"{'=' * 86}\n")

    row("", name1[:col_w - 1], name2[:col_w - 1])
    print(f"  {'-' * 24} {'-' * col_w} {'-' * col_w}")

    row("District",
        s1.get("district", {}).get("districtName", "N/A")[:col_w - 1],
        s2.get("district", {}).get("districtName", "N/A")[:col_w - 1])

    row("Grades",
        f"{s1.get('lowGrade', '?')}–{s1.get('highGrade', '?')}",
        f"{s2.get('lowGrade', '?')}–{s2.get('highGrade', '?')}")

    row("Enrollment",
        fmt(l1.get("numberOfStudents")),
        fmt(l2.get("numberOfStudents")))

    row("Student/Teacher Ratio",
        fmt(l1.get("pupilTeacherRatio"), ":1"),
        fmt(l2.get("pupilTeacherRatio"), ":1"))

    # Rank percentile: rank / rankOf * 100 (lower rank number = better)
    def rank_pct(r: dict) -> str:
        rank = r.get("rank")
        rank_of = r.get("rankOf")
        if rank and rank_of:
            percentile = (1 - rank / rank_of) * 100
            return f"Top {100 - percentile:.0f}% ({rank} of {rank_of})"
        return "N/A"

    row("Rank Percentile", rank_pct(r1), rank_pct(r2))

    # Stars are on a 0-5 scale
    row("Stars (0-5)",
        fmt(r1.get("rankStars")),
        fmt(r2.get("rankStars")))

    row("Free/Reduced Lunch",
        fmt(l1.get("percentFreeDiscLunch"), "%"),
        fmt(l2.get("percentFreeDiscLunch"), "%"))

    # Test scores comparison — newest entry per (subject, grade) for each school
    # grade '14' is SchoolDigger's code for school-wide composite score
    def grade_label(g: str) -> str:
        return "All" if str(g) == "14" else str(g) if g else "All"

    def newest_by_key(scores: list) -> dict:
        result: dict = {}
        for ts in sorted(scores, key=lambda t: t.get("year", 0), reverse=True):
            key = (ts.get("subject"), ts.get("grade"))
            if key not in result:
                result[key] = ts
        return result

    print(f"\n  --- Test Scores ---\n")
    ts1 = newest_by_key(s1.get("testScores", []))
    ts2 = newest_by_key(s2.get("testScores", []))
    keys = sorted(set(ts1.keys()) | set(ts2.keys()))

    ts_lbl_w = 30  # wider than main rows to fit "English Language Arts Gr.All"
    if keys:
        print(f"  {'Subject / Grade':<{ts_lbl_w}} {'% Met Standard':<{col_w}} {'% Met Standard':<{col_w}}")
        print(f"  {'-' * ts_lbl_w} {'-' * col_w} {'-' * col_w}")
        shown = 0
        for key in keys:
            subj, grade = key
            t1 = ts1.get(key, {}).get("schoolTestScore", {})
            t2 = ts2.get(key, {}).get("schoolTestScore", {})
            v1 = fmt(t1.get("percentMetStandard"), "%")
            v2 = fmt(t2.get("percentMetStandard"), "%")
            label = f"{subj} Gr.{grade_label(grade)}"
            print(f"  {label[:ts_lbl_w]:<{ts_lbl_w}} {v1:<{col_w}} {v2:<{col_w}}")
            shown += 1
            if shown >= 8:
                break
    else:
        print("  No test score data available for comparison.")


def main() -> None:
    app_id, app_key = get_credentials()

    school_id_1 = sys.argv[1] if len(sys.argv) > 1 else "530792001309"
    school_id_2 = sys.argv[2] if len(sys.argv) > 2 else "530792003116"

    print(f"Comparing schools: {school_id_1} vs {school_id_2}...")

    try:
        s1 = get_school(school_id_1, app_id, app_key)
        s2 = get_school(school_id_2, app_id, app_key)
        display_comparison(s1, s2)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
