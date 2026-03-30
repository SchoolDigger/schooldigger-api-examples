/**
 * Express.js proxy server for the SchoolDigger K-12 School Data API.
 *
 * Provides two endpoints that proxy requests to SchoolDigger, keeping
 * your API credentials server-side and out of the browser.
 *
 *   GET /api/schools?st=WA&q=Lincoln   — search schools
 *   GET /api/schools/:id               — get full school detail
 *
 * Usage:
 *   export SCHOOLDIGGER_APP_ID=your_app_id
 *   export SCHOOLDIGGER_APP_KEY=your_app_key
 *   npm install
 *   node express_school_lookup.mjs
 *
 * Then open: http://localhost:3000/api/schools?st=WA&q=Lincoln
 *
 * PRODUCTION NOTE: This is a demo. In production you should:
 *   - Cache API responses (e.g. Redis) to reduce API call volume
 *   - Never expose your appID/appKey to the browser
 *   - Add rate limiting to protect your API quota
 *   - Store credentials in a secrets manager, not environment variables
 *
 * Requires Node.js 18+.
 */

import express from "express";

const API_BASE = "https://api.schooldigger.com/v2.3";
const PORT = 3000;

function getCredentials() {
  const appID = process.env.SCHOOLDIGGER_APP_ID;
  const appKey = process.env.SCHOOLDIGGER_APP_KEY;
  if (!appID || !appKey) {
    console.error("Error: Set SCHOOLDIGGER_APP_ID and SCHOOLDIGGER_APP_KEY environment variables.");
    process.exit(1);
  }
  return { appID, appKey };
}

const { appID, appKey } = getCredentials();
const app = express();

// CORS headers — allow any origin for demo purposes
app.use((req, res, next) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Headers", "Content-Type");
  next();
});

/**
 * GET /api/schools?st=WA&q=Lincoln&page=1&perPage=10
 * Proxies to SchoolDigger school search endpoint.
 */
app.get("/api/schools", async (req, res) => {
  try {
    const forward = new URLSearchParams({ ...req.query, appID, appKey });
    const upstream = await fetch(`${API_BASE}/schools?${forward}`);
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/schools/:id
 * Proxies to SchoolDigger school detail endpoint.
 * Returns full school record including test scores, rankings, demographics.
 */
app.get("/api/schools/:id", async (req, res) => {
  try {
    const params = new URLSearchParams({ appID, appKey });
    const upstream = await fetch(`${API_BASE}/schools/${req.params.id}?${params}`);
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`SchoolDigger proxy running on http://localhost:${PORT}`);
  console.log(`Try: http://localhost:${PORT}/api/schools?st=WA&q=Lincoln`);
  console.log(`Try: http://localhost:${PORT}/api/schools/530792001309`);
});
