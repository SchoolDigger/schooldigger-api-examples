/**
 * Fetch and display a full school profile from the SchoolDigger API.
 *
 * Retrieves detailed information for a school including demographics,
 * rank history, and test scores.
 *
 * Usage:
 *   export SCHOOLDIGGER_APP_ID=your_app_id
 *   export SCHOOLDIGGER_APP_KEY=your_app_key
 *   node get_school_detail.mjs [school_id]
 *
 *   Default school ID: 530792001309 (Lake Forest Park Elementary, WA)
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

async function getSchool(schoolId, appID, appKey) {
  const params = new URLSearchParams({ appID, appKey });
  const res = await fetch(`${API_BASE}/schools/${schoolId}?${params}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

// SchoolDigger year convention: year 2025 = 2024-25 school year
function yearLabel(year) {
  return year ? `${year - 1}-${String(year).slice(2)}` : "N/A";
}

function fmt(val, suffix = "") {
  if (val == null) return "N/A";
  return typeof val === "number" ? `${val.toFixed(1)}${suffix}` : `${val}${suffix}`;
}

function displaySchool(school) {
  const addr = school.address ?? {};
  const addressStr = [addr.street, addr.city, addr.state, addr.zip].filter(Boolean).join(", ");
  const district = school.district?.districtName ?? "N/A";

  const yearly = school.schoolYearlyDetails ?? [];
  const latest = yearly[0] ?? {};
  const yl = yearLabel(latest.year);

  console.log(`\n${"=".repeat(60)}`);
  console.log(`  ${school.schoolName}`);
  console.log(`${"=".repeat(60)}`);
  console.log(`  Address:    ${addressStr}`);
  console.log(`  District:   ${district}`);
  console.log(`  Grades:     ${school.lowGrade ?? "?"} – ${school.highGrade ?? "?"}`);
  console.log(`  Enrollment: ${latest.numberOfStudents ?? "N/A"} (${yl})`);
  console.log(`  Pupil/Teacher Ratio: ${fmt(latest.pupilTeacherRatio)}`);
  if (latest.percentFreeDiscLunch != null) {
    console.log(`  Free/Reduced Lunch:  ${fmt(latest.percentFreeDiscLunch, "%")}`);
  }

  // Use urlSchoolDigger from the API response for the school's page URL
  const sdUrl = school.urlSchoolDigger || school.url;
  if (sdUrl) console.log(`\n  SchoolDigger page: ${sdUrl}`);

  // Demographics — field names from the SchoolDigger API response
  console.log(`\n--- Demographics (${yl}) ---\n`);
  const demoFields = [
    ["percentofWhiteStudents",           "White"],
    ["percentofAfricanAmericanStudents", "Black"],
    ["percentofHispanicStudents",        "Hispanic"],
    ["percentofAsianStudents",           "Asian"],
    ["percentofIndianStudents",          "American Indian"],
    ["percentofPacificIslanderStudents", "Pacific Islander"],
    ["percentofTwoOrMoreRaceStudents",   "Two or More Races"],
  ];
  console.log(`  ${"Group".padEnd(22)} ${"Percent".padStart(8)}`);
  console.log(`  ${"-".repeat(22)} ${"-".repeat(8)}`);
  for (const [field, label] of demoFields) {
    const val = latest[field];
    if (val != null) {
      console.log(`  ${label.padEnd(22)} ${val.toFixed(1).padStart(7)}%`);
    }
  }

  // Rank history (last 5 years)
  const rankHistory = school.rankHistory ?? [];
  if (rankHistory.length > 0) {
    const count = Math.min(5, rankHistory.length);
    console.log(`\n--- Rank History (last ${count} years) ---\n`);
    console.log(`  ${"Year".padEnd(12)} ${"Rank".padEnd(16)} Stars`);
    console.log(`  ${"-".repeat(12)} ${"-".repeat(16)} ${"-".repeat(5)}`);
    for (const r of rankHistory.slice(0, 5)) {
      // rankStars is on a 0-5 scale
      const yrLabel = yearLabel(r.year);
      const rankStr = `${r.rank} of ${r.rankOf}`;
      console.log(`  ${yrLabel.padEnd(12)} ${rankStr.padEnd(16)} ${r.rankStars ?? "N/A"}`);
    }
  }

  // Test scores
  const testScores = school.testScores ?? [];
  if (testScores.length > 0) {
    console.log(`\n--- Test Scores (most recent) ---\n`);
    console.log(`  ${"Subject".padEnd(14)} ${"Grade".padEnd(8)} ${"Year".padEnd(10)} ${"% Met Standard".padStart(15)}`);
    console.log(`  ${"-".repeat(14)} ${"-".repeat(8)} ${"-".repeat(10)} ${"-".repeat(15)}`);
    const shown = new Set();
    for (const ts of testScores) {
      const key = `${ts.subject}|${ts.grade}`;
      if (shown.has(key)) continue;
      shown.add(key);
      const pct = ts.schoolTestScore?.percentMetStandard;
      const pctStr = pct != null ? `${pct.toFixed(1)}%` : "N/A";
      console.log(`  ${String(ts.subject ?? "").padEnd(14)} ${String(ts.grade ?? "All").padEnd(8)} ${yearLabel(ts.year).padEnd(10)} ${pctStr.padStart(15)}`);
      if (shown.size >= 10) break;
    }
  } else {
    console.log("\n  No test score data available.");
  }
}

async function main() {
  const { appID, appKey } = getCredentials();
  const schoolId = process.argv[2] ?? "530792001309";

  console.log(`Fetching school detail for ID: ${schoolId}...`);

  try {
    const school = await getSchool(schoolId, appID, appKey);
    displaySchool(school);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
