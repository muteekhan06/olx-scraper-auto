const { getGithubConfig, githubRequest, json, readJsonBody, requireAuth } = require("./_lib/auth");
const { KARACHI_AREA_KEYS } = require("./_lib/karachi");

function sanitizeAreas(input) {
  if (!Array.isArray(input)) {
    return [];
  }
  const out = [];
  for (const raw of input) {
    const key = String(raw || "").trim().toLowerCase();
    if (!key) {
      continue;
    }
    if (!KARACHI_AREA_KEYS.has(key)) {
      throw new Error(`Invalid area key: ${key}`);
    }
    if (!out.includes(key)) {
      out.push(key);
    }
  }
  return out;
}

function clampInt(value, min, max, fallback) {
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, n));
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }

  const session = requireAuth(req, res);
  if (!session) {
    return;
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (err) {
    json(res, 400, { error: err.message });
    return;
  }

  let areas;
  try {
    areas = sanitizeAreas(body.areas);
  } catch (err) {
    json(res, 400, { error: err.message });
    return;
  }

  if (areas.length === 0) {
    json(res, 400, { error: "Select at least one Karachi area." });
    return;
  }

  const maxPages = clampInt(body.maxPages, 1, 10, 2);
  const maxListings = clampInt(body.maxListings, 1, 50, 15);
  const cfg = getGithubConfig();

  try {
    await githubRequest(
      `/repos/${cfg.owner}/${cfg.repo}/actions/workflows/${cfg.workflowFile}/dispatches`,
      {
        method: "POST",
        body: {
          ref: cfg.ref,
          inputs: {
            areas: areas.join(","),
            max_pages: String(maxPages),
            max_listings: String(maxListings)
          }
        }
      }
    );

    json(res, 200, {
      ok: true,
      message: "Karachi workflow dispatched successfully.",
      areas,
      maxPages,
      maxListings
    });
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};

