/**
 * Demonstrate the SchoolDigger autocomplete endpoint for typeahead UIs.
 *
 * Accepts a partial school name and returns matching schools with their IDs.
 * This powers instant search / typeahead features in web apps — call this
 * endpoint on each keystroke (debounced) to show suggestions as the user types.
 *
 * Usage:
 *   export SCHOOLDIGGER_APP_ID=your_app_id
 *   export SCHOOLDIGGER_APP_KEY=your_app_key
 *   node autocomplete_demo.mjs [partial_name] [state]
 *
 *   Examples:
 *     node autocomplete_demo.mjs "Linco" WA
 *     node autocomplete_demo.mjs "lake forest"
 *
 * Requires Node.js 18+ (uses native fetch).
 */

const API_BASE = "https://api.schooldigger.com/v2.3";

function getCredentials() {
  const appID = process.env.SCHOOLDIGGER_APP_ID;
  const appKey = process.env.SCHOOLDIGGER_APP_KEY;
  if (!appID || !appKey) {
    console.error("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.");
    console.error("Get a free API key at https://developer.schooldigger.com");
    process.exit(1);
  }
  return { appID, appKey };
}

async function autocomplete(query, state, appID, appKey) {
  const params = new URLSearchParams({ q: query, st: state, appID, appKey });
  const res = await fetch(`${API_BASE}/autocomplete/schools?${params}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

function displayMatches(data, query) {
  const matches = data.schoolMatches ?? [];

  if (matches.length === 0) {
    console.log(`No schools matched "${query}".`);
    return;
  }

  console.log(`\n${matches.length} match(es) for "${query}":\n`);
  console.log(`  ${"School ID".padEnd(14)} ${"School Name".padEnd(40)} City`);
  console.log(`  ${"-".repeat(14)} ${"-".repeat(40)} ${"-".repeat(20)}`);

  for (const m of matches) {
    const id   = String(m.schoolid ?? "").padEnd(14);
    const name = String(m.schoolName ?? "").slice(0, 39).padEnd(40);
    const city = m.city ?? "";
    console.log(`  ${id} ${name} ${city}`);
  }

  console.log(`\nHow to use school IDs:`);
  console.log(`  GET /v2.3/schools/{schoolid} — fetch the full school profile`);
  console.log(`  e.g. node get_school_detail.mjs ${matches[0]?.schoolid ?? "530792001309"}`);
}

async function main() {
  const { appID, appKey } = getCredentials();
  const query = process.argv[2] ?? "Linco";
  const state = process.argv[3] ?? "WA";

  console.log(`Autocomplete: "${query}" in ${state}...`);

  try {
    const data = await autocomplete(query, state, appID, appKey);
    displayMatches(data, query);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
