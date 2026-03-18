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

function normalizeFilterTokens(rawInput) {
  const raw = String(rawInput || "").trim();
  if (!raw) {
    return "";
  }

  let tokenString = raw;
  if (/^https?:\/\//i.test(raw)) {
    try {
      const u = new URL(raw);
      tokenString = u.searchParams.get("filter") || "";
    } catch (_err) {
      throw new Error("Invalid custom URL provided for filter parsing.");
    }
  } else if (raw.startsWith("?")) {
    const qp = new URLSearchParams(raw.slice(1));
    tokenString = qp.get("filter") || "";
  } else if (raw.includes("filter=")) {
    const qp = new URLSearchParams(raw.replace(/^\?/, ""));
    tokenString = qp.get("filter") || "";
  }

  const tokens = [];
  for (const part of tokenString.split(",")) {
    const token = String(part || "").trim().toLowerCase();
    if (!token) {
      continue;
    }
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(token)) {
      throw new Error(`Invalid filter token: ${token}`);
    }
    if (!tokens.includes(token)) {
      tokens.push(token);
    }
  }

  return tokens.join(",");
}

function normalizeCustomSearchUrl(rawInput) {
  const raw = String(rawInput || "").trim();
  if (!raw) {
    return "";
  }
  let u;
  try {
    u = new URL(raw);
  } catch (_err) {
    throw new Error("customSearchUrl must be a valid URL.");
  }
  if (u.hostname !== "www.olx.com.pk") {
    throw new Error("customSearchUrl must use www.olx.com.pk domain.");
  }
  if (!u.pathname.includes("/cars_c84")) {
    throw new Error("customSearchUrl must point to a cars_c84 listing URL.");
  }
  return u.toString();
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

  const maxPages = clampInt(body.maxPages, 1, 10, 2);
  const maxListings = clampInt(body.maxListings, 1, 50, 15);
  const githubToken = String(body.githubToken || "").trim();
  let areas;
  try {
    areas = sanitizeAreas(body.areas);
  } catch (err) {
    json(res, 400, { error: err.message });
    return;
  }
  let filterTokens;
  let customSearchUrl;
  try {
    filterTokens = normalizeFilterTokens(body.filterTokens);
    customSearchUrl = normalizeCustomSearchUrl(body.customSearchUrl);
  } catch (err) {
    json(res, 400, { error: err.message });
    return;
  }

  if (areas.length === 0 && !customSearchUrl) {
    json(res, 400, { error: "Select at least one Karachi area or provide customSearchUrl." });
    return;
  }

  const cfg = getGithubConfig(githubToken);

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
            max_listings: String(maxListings),
            filter_tokens: filterTokens,
            custom_search_url: customSearchUrl
          }
        }
      },
      githubToken
    );

    json(res, 200, {
      ok: true,
      message: "Karachi workflow dispatched successfully.",
      areas,
      maxPages,
      maxListings,
      filterTokens,
      customSearchUrl
    });
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};
