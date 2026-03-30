/**
 * Search schools using the SchoolDigger API.
 *
 * Searches for schools in a given state matching a keyword and displays
 * results in a formatted table.
 *
 * Usage:
 *   export SCHOOLDIGGER_APP_ID=your_app_id
 *   export SCHOOLDIGGER_APP_KEY=your_app_key
 *   node search_schools.mjs
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

async function searchSchools(state, query, appID, appKey) {
  const params = new URLSearchParams({ st: state, q: query, appID, appKey });
  const res = await fetch(`${API_BASE}/schools?${params}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

function pad(str, len) {
  return String(str ?? "N/A").slice(0, len).padEnd(len);
}

function displayResults(data) {
  const schools = data.schoolList ?? [];
  const total = data.numberOfSchools ?? 0;

  if (schools.length === 0) {
    console.log("No schools found.");
    return;
  }

  console.log(`\nFound ${total} school(s). Showing first ${schools.length}:\n`);

  const header = `${"School Name".padEnd(40)} ${"City".padEnd(18)} ${"Grades".padEnd(10)} ${"Rank".padEnd(14)} ${"Stars".padEnd(6)} Students`;
  console.log(header);
  console.log("-".repeat(header.length));

  for (const school of schools) {
    const name = pad(school.schoolName, 40);
    const city = pad(school.address?.city, 18);
    const grades = pad(`${school.lowGrade ?? "?"}-${school.highGrade ?? "?"}`, 10);

    // rankStars is on a 0-5 scale; rank history sorted most-recent first
    const r = school.rankHistory?.[0];
    const rank = pad(r ? `${r.rank} of ${r.rankOf}` : "N/A", 14);
    const stars = pad(r?.rankStars, 6);

    const students = school.schoolYearlyDetails?.[0]?.numberOfStudents ?? "N/A";

    console.log(`${name} ${city} ${grades} ${rank} ${stars} ${students}`);
  }
}

async function main() {
  const { appID, appKey } = getCredentials();
  const state = "WA";
  const query = "Lincoln";

  console.log(`Searching for '${query}' schools in ${state}...`);

  try {
    const data = await searchSchools(state, query, appID, appKey);
    displayResults(data);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
