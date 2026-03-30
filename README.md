# SchoolDigger API Examples

Code examples for the [SchoolDigger K-12 School Data API](https://developer.schooldigger.com) — the most comprehensive source of U.S. school data available via API.

## What is SchoolDigger?

SchoolDigger provides data on **130,000+ U.S. public, charter, and private schools** and **18,500+ districts** across all 50 states. Since 2006, SchoolDigger has been trusted by Harvard, Money Magazine, Century 21, IXL, Precisely, Coldwell Banker, and Franklin Covey.

### Data Available

| Category | Details | History |
|----------|---------|---------|
| **School Directory** | Name, address, phone, lat/long, grades served, charter/magnet/virtual flags | Current |
| **Demographics** | Enrollment, racial breakdown, free/reduced lunch %, student/teacher ratio | 20 years |
| **Test Scores** | 20M+ records — proficiency rates by school/district/state, grade, subject | 10 years |
| **Rankings** | SchoolDigger 0-5 star rankings for schools and districts | 10+ years |
| **Finance** | Per-pupil expenditures (federal vs state/local split) | 5 years |
| **Outcomes** | Graduation rates, dropout rates, chronic absenteeism | 5 years |
| **Boundaries** | District attendance boundary polygons (Pro/Enterprise) | Current |
| **Reviews** | Parent/community ratings and comments | Ongoing |

### API at a Glance

| | |
|---|---|
| **Base URL** | `https://api.schooldigger.com/v2.3` |
| **Format** | JSON |
| **Auth** | `appID` + `appKey` query parameters |
| **Free Tier** | DEV/TEST — Enterprise-level data, 20 calls/day, no credit card |
| **Docs** | [Interactive docs](https://developer.schooldigger.com/docs) · [Swagger spec](https://api.schooldigger.com/swagger/docs/v2.3) · [LLM reference](https://developer.schooldigger.com/llms-full.txt) |
| **Pricing** | Free → $19.90/mo → $89/mo → $189/mo |

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /v2.3/schools` | Search schools by state, city, zip, name, location, type |
| `GET /v2.3/schools/{id}` | Full school record with test scores, finance, reviews, rank history |
| `GET /v2.3/districts` | Search districts by state, city, zip, name, location |
| `GET /v2.3/districts/{id}` | Full district record with boundaries, test scores, finance |
| `GET /v2.3/rankings/schools/{st}` | Statewide school ranking list |
| `GET /v2.3/rankings/districts/{st}` | Statewide district ranking list |
| `GET /v2.3/autocomplete/schools` | Fast typeahead school search |
| `GET /v2.3/autocomplete/districts` | Fast typeahead district search |

## Quick Start

1. **Get a free API key** at [developer.schooldigger.com](https://developer.schooldigger.com) (no credit card required)
2. **Set environment variables:**
   ```bash
   export SCHOOLDIGGER_APP_ID=your_app_id
   export SCHOOLDIGGER_APP_KEY=your_app_key
   ```
3. **Run an example:**
   ```bash
   # Python
   cd python && pip install -r requirements.txt && python search_schools.py

   # JavaScript
   cd javascript && npm install && node search_schools.mjs

   # curl
   curl "https://api.schooldigger.com/v2.3/schools?st=WA&q=Lincoln&appID=$SCHOOLDIGGER_APP_ID&appKey=$SCHOOLDIGGER_APP_KEY"
   ```

## Examples

### Python

| File | Description |
|------|-------------|
| `search_schools.py` | Search schools by state and keyword, display results |
| `get_school_detail.py` | Fetch full school profile including test scores and demographics |
| `compare_schools.py` | Compare two schools side-by-side (rankings, test scores, demographics) |
| `find_nearby_schools.py` | Find schools near a latitude/longitude (Pro/Enterprise) |
| `export_rankings_csv.py` | Export a state's school rankings to CSV |

### JavaScript

| File | Description |
|------|-------------|
| `search_schools.mjs` | Search schools and display results |
| `get_school_detail.mjs` | Fetch and display a full school profile |
| `autocomplete_demo.mjs` | Demonstrate the autocomplete endpoint for typeahead UIs |
| `express_school_lookup.mjs` | Express.js server with a school search endpoint |

### R

| File | Description |
|------|-------------|
| `search_schools.R` | Search schools and create a data frame |
| `plot_school_demographics.R` | Fetch a state's rankings and plot demographic breakdowns with ggplot2 |

### C#

| File | Description |
|------|-------------|
| `Program.cs` | .NET console app demonstrating school search and detail retrieval |

### curl

| File | Description |
|------|-------------|
| `examples.sh` | Annotated curl commands for every endpoint |

## Common Use Cases

- **Real estate apps** — Display nearby school ratings on property listings
- **School choice tools** — Help parents compare schools by test scores, demographics, and rankings
- **Education research** — Analyze performance trends across schools, districts, or states
- **EdTech platforms** — Enrich your product with school directory and performance data
- **Data journalism** — Investigate school spending, achievement gaps, or demographic shifts

## Other Ways to Access SchoolDigger Data

| Method | Best For | Link |
|--------|----------|------|
| **API** | Real-time integration into apps and websites | [developer.schooldigger.com](https://developer.schooldigger.com) |
| **Widgets** | No-code embeds for any website | [widgets.schooldigger.com](https://widgets.schooldigger.com) |
| **AWS Marketplace** | Bulk data download (CSV/tab-delimited) | [AWS Seller Profile](https://aws.amazon.com/marketplace/seller-profile?id=118e43c1-dba6-4716-a1c0-b37d9bc37a37) |
| **Snowflake Marketplace** | Query in your Snowflake warehouse | [Snowflake Listing](https://app.snowflake.com/marketplace/listing/GZTYZ13NE7HJ5) |
| **RapidAPI** | Alternative API gateway | [RapidAPI Listing](https://rapidapi.com/schooldigger-schooldigger-default/api/schooldigger-k-12-school-data-api) |

## Support

- **Email:** api@schooldigger.com
- **Documentation:** [developer.schooldigger.com/docs](https://developer.schooldigger.com/docs)
- **LLM Integration:** [llms.txt](https://developer.schooldigger.com/llms.txt) · [Full LLM reference](https://developer.schooldigger.com/llms-full.txt)

## License

These examples are MIT licensed. The SchoolDigger API itself requires an API key — [get one free](https://developer.schooldigger.com).

