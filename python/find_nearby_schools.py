"""
Find schools near a geographic location using the SchoolDigger API.

Searches for schools within a given radius of a latitude/longitude
and displays results sorted by distance.

NOTE: The nearLatitude/nearLongitude parameters require a Pro or
Enterprise API plan. See https://developer.schooldigger.com for details.

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python find_nearby_schools.py [latitude] [longitude] [radius_miles]

    Defaults: lat=47.7631, lon=-122.2878 (Lake Forest Park, WA), radius=5
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


def find_nearby(
    state: str,
    lat: float,
    lon: float,
    radius: float,
    app_id: str,
    app_key: str,
) -> dict:
    """Search for schools near a geographic point."""
    url = f"{API_BASE}/schools"
    params = {
        "st": state,
        "nearLatitude": lat,
        "nearLongitude": lon,
        "distanceMiles": radius,
        "appID": app_id,
        "appKey": app_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def display_results(data: dict, lat: float, lon: float, radius: float) -> None:
    """Print nearby schools sorted by distance."""
    schools = data.get("schoolList", [])
    total = data.get("numberOfSchools", 0)

    if not schools:
        print("No schools found in the specified area.")
        print("Note: Location search requires a Pro or Enterprise plan.")
        return

    print(f"\nFound {total} school(s) within {radius} miles of ({lat}, {lon}).")
    print(f"Showing first {len(schools)}:\n")

    # Sort by distance if available
    schools.sort(key=lambda s: s.get("distance", float("inf")))

    header = f"{'School Name':<36} {'City':<16} {'Grades':<8} {'Distance':<10} {'Stars':<6}"
    print(header)
    print("-" * len(header))

    for school in schools:
        name = school.get("schoolName", "N/A")[:35]
        city = school.get("address", {}).get("city", "N/A")[:15]
        low = school.get("lowGrade", "?")
        high = school.get("highGrade", "?")
        grades = f"{low}-{high}"

        distance = school.get("distance")
        dist_str = f"{distance:.1f} mi" if distance is not None else "N/A"

        rank_history = school.get("rankHistory", [])
        stars = str(rank_history[0].get("rankStars", "N/A")) if rank_history else "N/A"

        print(f"{name:<36} {city:<16} {grades:<8} {dist_str:<10} {stars:<6}")


def main() -> None:
    app_id, app_key = get_credentials()

    # Default location: Lake Forest Park, WA
    lat = float(sys.argv[1]) if len(sys.argv) > 1 else 47.7631
    lon = float(sys.argv[2]) if len(sys.argv) > 2 else -122.2878
    radius = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0

    # Determine state from default; in a real app you'd geocode or accept as input
    state = "WA"

    print(f"Searching for schools within {radius} miles of ({lat}, {lon}) in {state}...")
    print("Note: Location-based search requires a Pro or Enterprise API plan.\n")

    try:
        data = find_nearby(state, lat, lon, radius, app_id, app_key)
        display_results(data, lat, lon, radius)
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e.response.status_code} — {e.response.text}")
        if e.response.status_code == 401:
            print("This may require a Pro or Enterprise plan for location-based search.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
