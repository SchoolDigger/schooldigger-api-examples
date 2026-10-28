"""
Fetch many school records at once with the SchoolDigger async batch API.

POST https://api.schooldigger.com/batches with a list of API paths (up to 2,000).
SchoolDigger runs the calls for you, paced at half your plan's per-minute limit,
and you download the results in parts of 20 as each part finishes. Each item
counts as one API call; submitting, polling and downloading are free.
Paid plans only (Developer/DEMO keys get 403).

The Python SDK has the same flow built in:
    from schooldigger.batch import BatchClient
    client = BatchClient(app_id, app_key)
    batch = client.submit_batch(paths)
    for part in client.wait_for_batch(batch["batchId"]): ...

Usage:
    export SCHOOLDIGGER_APP_ID=your_app_id
    export SCHOOLDIGGER_APP_KEY=your_app_key
    python batch_school_details.py [school_id ...]

    Default school IDs: 530792001309 (Lake Forest Park Elementary, WA),
    530792003116 (Cascade K-8, WA), 530111000200 (Progress Elementary, WA)

Guide: https://developer.schooldigger.com/batch-requests-schooldigger-api
"""

import json
import os
import sys
import time
import requests


BASE = "https://api.schooldigger.com"
DEFAULT_IDS = ["530792001309", "530792003116", "530111000200"]


def get_credentials() -> dict:
    """Read API credentials from environment variables."""
    app_id = os.environ.get("SCHOOLDIGGER_APP_ID")
    app_key = os.environ.get("SCHOOLDIGGER_APP_KEY")
    if not app_id or not app_key:
        print("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.")
        print("Get an API key at https://developer.schooldigger.com")
        sys.exit(1)
    return {"appID": app_id, "appKey": app_key}


def check(response: requests.Response) -> dict:
    """Return the JSON body, or exit with the API's error message."""
    if response.status_code >= 400:
        err = response.json()
        print(f"Error {response.status_code}: {err.get('message')} - {err.get('description')}")
        for line in err.get("errors", []):
            print(f"  {line}")
        sys.exit(1)
    return response.json()


def main():
    creds = get_credentials()
    ids = sys.argv[1:] or DEFAULT_IDS

    # 1. Submit: each item is your own id plus an API path (no appID/appKey in it).
    items = [{"id": sid, "path": f"/v3.1/schools/{sid}"} for sid in ids]
    batch = check(requests.post(f"{BASE}/batches", params=creds, json={"items": items}))
    batch_id = batch["batchId"]
    print(f"Submitted {batch_id}: {batch['itemCount']} items in {batch['partCount']} part(s), "
          f"about {batch['estimatedSeconds']}s once it starts")

    # 2. Poll, waiting Retry-After seconds, and download each part as soon as it is ready.
    downloaded = set()
    while True:
        r = requests.get(f"{BASE}/batches/{batch_id}", params=creds)
        status = check(r)
        print(f"  {status['status']}: {status['completedCount']}/{status['itemCount']} done")

        for part in status["partsReady"]:
            if part in downloaded:
                continue
            # 3. Each part is gzipped NDJSON; requests unzips it (Content-Encoding: gzip).
            res = requests.get(f"{BASE}/batches/{batch_id}/results", params={**creds, "part": part})
            for line in res.text.splitlines():
                result = json.loads(line)
                body = result["body"] or {}
                if result["status"] == 200:
                    city = (body.get("address") or {}).get("city")
                    print(f"  [{result['id']}] {body.get('schoolName')} - {city}")
                else:
                    print(f"  [{result['id']}] HTTP {result['status']}: {body.get('message') or result.get('error')}")
            downloaded.add(part)

        if status["status"] not in ("queued", "running"):
            break
        time.sleep(int(r.headers.get("Retry-After", 15)))

    print(f"Batch {status['status']}: {status['itemCount'] - status['failedCount']} ok, "
          f"{status['failedCount']} failed. Results are kept until {status['expiresUtc']}.")


if __name__ == "__main__":
    main()
