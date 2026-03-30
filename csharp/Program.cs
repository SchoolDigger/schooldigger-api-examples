// SchoolDigger API Example — C# / .NET 8
//
// Demonstrates searching for schools and retrieving a full school profile
// using the SchoolDigger K-12 School Data API.
//
// Usage:
//   set SCHOOLDIGGER_APP_ID=your_app_id
//   set SCHOOLDIGGER_APP_KEY=your_app_key
//   dotnet run
//
// Get a free API key at https://developer.schooldigger.com

using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Nodes;

const string ApiBase = "https://api.schooldigger.com/v2.3";

// Read credentials from environment variables
string appId  = Environment.GetEnvironmentVariable("SCHOOLDIGGER_APP_ID")
    ?? throw new InvalidOperationException(
        "Set SCHOOLDIGGER_APP_ID environment variable. " +
        "Get a free key at https://developer.schooldigger.com");

string appKey = Environment.GetEnvironmentVariable("SCHOOLDIGGER_APP_KEY")
    ?? throw new InvalidOperationException(
        "Set SCHOOLDIGGER_APP_KEY environment variable.");

using var http = new HttpClient();

// ── School Search ───────────────────────────────────────────────────────────

string state = "WA";
string query = "Lincoln";

Console.WriteLine($"Searching for '{query}' schools in {state}...\n");

var searchUrl = $"{ApiBase}/schools?st={state}&q={Uri.EscapeDataString(query)}&appID={appId}&appKey={appKey}";
var searchJson = await http.GetFromJsonAsync<JsonObject>(searchUrl)
    ?? throw new Exception("Empty response from search endpoint.");

int total = searchJson["numberOfSchools"]?.GetValue<int>() ?? 0;
var schoolList = searchJson["schoolList"]?.AsArray() ?? new JsonArray();

Console.WriteLine($"Found {total} school(s). Showing first {schoolList.Count}:\n");
Console.WriteLine($"{"School Name",-40} {"City",-18} {"Grades",-10} {"Rank",-14} {"Stars",-6} Students");
Console.WriteLine(new string('-', 96));

foreach (var s in schoolList)
{
    string name    = s?["schoolName"]?.GetValue<string>() ?? "N/A";
    string city    = s?["address"]?["city"]?.GetValue<string>() ?? "N/A";
    string low     = s?["lowGrade"]?.GetValue<string>() ?? "?";
    string high    = s?["highGrade"]?.GetValue<string>() ?? "?";
    string grades  = $"{low}-{high}";

    // Rank history: most-recent year first; rankStars is on a 0-5 scale
    var rh    = s?["rankHistory"]?.AsArray();
    string rank  = rh?.Count > 0 ? $"{rh[0]?["rank"]} of {rh[0]?["rankOf"]}" : "N/A";
    string stars = rh?.Count > 0 ? rh[0]?["rankStars"]?.ToString() ?? "N/A" : "N/A";

    var yd  = s?["schoolYearlyDetails"]?.AsArray();
    string students = yd?.Count > 0 ? yd[0]?["numberOfStudents"]?.ToString() ?? "N/A" : "N/A";

    Console.WriteLine($"{name[..Math.Min(name.Length, 40)],-40} {city[..Math.Min(city.Length, 18)],-18} {grades,-10} {rank,-14} {stars,-6} {students}");
}

// ── School Detail ───────────────────────────────────────────────────────────

string defaultSchoolId = "530792001309"; // Lake Forest Park Elementary, WA
Console.WriteLine($"\n\nFetching detail for school ID: {defaultSchoolId}...\n");

var detailUrl = $"{ApiBase}/schools/{defaultSchoolId}?appID={appId}&appKey={appKey}";
var school = await http.GetFromJsonAsync<JsonObject>(detailUrl)
    ?? throw new Exception("Empty response from detail endpoint.");

string schoolName = school["schoolName"]?.GetValue<string>() ?? "N/A";
var addr  = school["address"];
string address = $"{addr?["street"]?.GetValue<string>()}, {addr?["city"]?.GetValue<string>()}, {addr?["state"]?.GetValue<string>()} {addr?["zip"]?.GetValue<string>()}";
string district = school["district"]?["districtName"]?.GetValue<string>() ?? "N/A";
string lowGrade  = school["lowGrade"]?.GetValue<string>() ?? "?";
string highGrade = school["highGrade"]?.GetValue<string>() ?? "?";

// Use urlSchoolDigger from API response for the school's page URL
string? sdUrl = school["urlSchoolDigger"]?.GetValue<string>() ?? school["url"]?.GetValue<string>();

var yearlyDetails = school["schoolYearlyDetails"]?.AsArray();
var latest = yearlyDetails?.Count > 0 ? yearlyDetails[0] : null;

// SchoolDigger year convention: year 2025 = 2024-25 school year
int? detailYear = latest?["year"]?.GetValue<int>();
string yearLabel = detailYear.HasValue ? $"{detailYear - 1}-{detailYear % 100:D2}" : "N/A";

Console.WriteLine($"{"=",0}{"".PadRight(60, '=')}");
Console.WriteLine($"  {schoolName}");
Console.WriteLine($"{"=",0}{"".PadRight(60, '=')}");
Console.WriteLine($"  Address:    {address}");
Console.WriteLine($"  District:   {district}");
Console.WriteLine($"  Grades:     {lowGrade} – {highGrade}");
Console.WriteLine($"  Enrollment: {latest?["numberOfStudents"]} ({yearLabel})");
Console.WriteLine($"  Pupil/Teacher Ratio: {latest?["pupilTeacherRatio"]}");
if (sdUrl is not null)
    Console.WriteLine($"\n  SchoolDigger page: {sdUrl}");

// Rank history
var rankHistory = school["rankHistory"]?.AsArray();
if (rankHistory?.Count > 0)
{
    Console.WriteLine($"\n--- Rank History (last {Math.Min(5, rankHistory.Count)} years) ---\n");
    Console.WriteLine($"  {"Year",-12} {"Rank",-16} Stars");
    Console.WriteLine($"  {new string('-', 12)} {new string('-', 16)} {new string('-', 5)}");
    foreach (var r in rankHistory.Take(5))
    {
        int? yr = r?["year"]?.GetValue<int>();
        string yrLabel = yr.HasValue ? $"{yr - 1}-{yr % 100:D2}" : "N/A";
        string rankStr = $"{r?["rank"]} of {r?["rankOf"]}";
        Console.WriteLine($"  {yrLabel,-12} {rankStr,-16} {r?["rankStars"]}");
    }
}

// Test scores (first 8 unique subject/grade combos)
var testScores = school["testScores"]?.AsArray();
if (testScores?.Count > 0)
{
    Console.WriteLine($"\n--- Test Scores (most recent) ---\n");
    Console.WriteLine($"  {"Subject",-14} {"Grade",-8} {"Year",-10} {"% Met Standard",15}");
    Console.WriteLine($"  {new string('-', 14)} {new string('-', 8)} {new string('-', 10)} {new string('-', 15)}");

    var seen = new HashSet<string>();
    foreach (var ts in testScores)
    {
        string subject = ts?["subject"]?.GetValue<string>() ?? "";
        string grade   = ts?["grade"]?.GetValue<string>() ?? "All";
        string key     = $"{subject}|{grade}";
        if (!seen.Add(key)) continue;

        int? tsYear = ts?["year"]?.GetValue<int>();
        string tsYearLabel = tsYear.HasValue ? $"{tsYear - 1}-{tsYear % 100:D2}" : "N/A";
        double? pct = ts?["schoolTestScore"]?["percentMetStandard"]?.GetValue<double>();
        string pctStr = pct.HasValue ? $"{pct:F1}%" : "N/A";

        Console.WriteLine($"  {subject,-14} {grade,-8} {tsYearLabel,-10} {pctStr,15}");
        if (seen.Count >= 8) break;
    }
}
