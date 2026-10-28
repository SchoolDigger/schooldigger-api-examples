/**
 * Fetch many school records at once with the SchoolDigger async batch API.
 *
 * POST https://api.schooldigger.com/batches with a list of API paths (up to 2,000).
 * SchoolDigger runs the calls for you, paced at half your plan's per-minute limit,
 * and you download the results in parts of 20 as each part finishes. Each item
 * counts as one API call; submitting, polling and downloading are free.
 * Paid plans only (Developer/DEMO keys get 403).
 *
 * The JS SDK has the same flow built in:
 *   import { BatchClient } from 'schooldigger';
 *   const client = new BatchClient({ appID, appKey });
 *   const batch = await client.submitBatch(paths);
 *   for await (const { part, results } of client.waitForBatch(batch.batchId)) { ... }
 *
 * Usage:
 *   export SCHOOLDIGGER_APP_ID=your_app_id
 *   export SCHOOLDIGGER_APP_KEY=your_app_key
 *   node batch_school_details.mjs [school_id ...]
 *
 * Requires Node.js 18+ (native fetch, which unzips the gzipped result parts).
 * Guide: https://developer.schooldigger.com/batch-requests-schooldigger-api
 */

const BASE = "https://api.schooldigger.com";
const DEFAULT_IDS = ["530792001309", "530792003116", "530111000200"];

function getCredentials() {
  const appID = process.env.SCHOOLDIGGER_APP_ID;
  const appKey = process.env.SCHOOLDIGGER_APP_KEY;
  if (!appID || !appKey) {
    console.error("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.");
    console.error("Get an API key at https://developer.schooldigger.com");
    process.exit(1);
  }
  return new URLSearchParams({ appID, appKey }).toString();
}

async function check(response) {
  const body = await response.json();
  if (response.status >= 400) {
    console.error(`Error ${response.status}: ${body.message} - ${body.description}`);
    for (const line of body.errors || []) console.error(`  ${line}`);
    process.exit(1);
  }
  return body;
}

const creds = getCredentials();
const ids = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_IDS;

// 1. Submit: each item is your own id plus an API path (no appID/appKey in it).
const items = ids.map(id => ({ id, path: `/v3.1/schools/${id}` }));
const batch = await check(await fetch(`${BASE}/batches?${creds}`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ items }),
}));
console.log(`Submitted ${batch.batchId}: ${batch.itemCount} items in ${batch.partCount} part(s), ` +
  `about ${batch.estimatedSeconds}s once it starts`);

// 2. Poll, waiting Retry-After seconds, and download each part as soon as it is ready.
const downloaded = new Set();
let status;
while (true) {
  const r = await fetch(`${BASE}/batches/${batch.batchId}?${creds}`);
  status = await check(r);
  console.log(`  ${status.status}: ${status.completedCount}/${status.itemCount} done`);

  for (const part of status.partsReady) {
    if (downloaded.has(part)) continue;
    // 3. Each part is gzipped NDJSON; fetch unzips it (Content-Encoding: gzip).
    const res = await fetch(`${BASE}/batches/${batch.batchId}/results?part=${part}&${creds}`);
    for (const line of (await res.text()).split("\n").filter(Boolean)) {
      const result = JSON.parse(line);
      const body = result.body || {};
      if (result.status === 200) {
        console.log(`  [${result.id}] ${body.schoolName} - ${body.address?.city}`);
      } else {
        console.log(`  [${result.id}] HTTP ${result.status}: ${body.message || result.error}`);
      }
    }
    downloaded.add(part);
  }

  if (!["queued", "running"].includes(status.status)) break;
  const wait = Number(r.headers.get("Retry-After") || 15);
  await new Promise(res => setTimeout(res, wait * 1000));
}

console.log(`Batch ${status.status}: ${status.itemCount - status.failedCount} ok, ` +
  `${status.failedCount} failed. Results are kept until ${status.expiresUtc}.`);
