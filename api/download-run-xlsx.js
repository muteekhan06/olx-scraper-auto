const AdmZip = require("adm-zip");

const { getGithubConfig, githubRequest, json, requireAuth } = require("./_lib/auth");

function parseQuery(req) {
  return new URL(req.url, "https://dashboard.local").searchParams;
}

function isPositiveInteger(value) {
  return /^\d+$/.test(String(value || ""));
}

function sanitizeFilename(name) {
  return String(name || "karachi-output.xlsx").replace(/[^A-Za-z0-9._-]/g, "_");
}

async function fetchArtifactZip(cfg, artifactId) {
  if (!cfg.token) {
    const err = new Error("GITHUB_PAT is missing.");
    err.status = 500;
    throw err;
  }

  const resp = await fetch(
    `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/actions/artifacts/${artifactId}/zip`,
    {
      headers: {
        Authorization: `Bearer ${cfg.token}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
      },
      redirect: "follow"
    }
  );

  if (!resp.ok) {
    const text = await resp.text();
    const err = new Error(`GitHub artifact download failed (${resp.status}): ${text}`);
    err.status = resp.status;
    throw err;
  }

  return Buffer.from(await resp.arrayBuffer());
}

function extractFirstXlsx(zipBuffer) {
  const zip = new AdmZip(zipBuffer);
  const entry = zip.getEntries().find((item) => !item.isDirectory && item.entryName.toLowerCase().endsWith(".xlsx"));

  if (!entry) {
    const err = new Error("No XLSX file found in this workflow artifact.");
    err.status = 404;
    throw err;
  }

  return {
    name: sanitizeFilename(entry.entryName.split("/").pop()),
    buffer: entry.getData()
  };
}

async function resolveArtifactId(cfg, runId) {
  const data = await githubRequest(
    `/repos/${cfg.owner}/${cfg.repo}/actions/runs/${runId}/artifacts?per_page=100`
  );

  const artifacts = (data.artifacts || []).filter((artifact) => !artifact.expired);
  const artifact =
    artifacts.find((item) => item.name === "scraper-xlsx-karachi") ||
    artifacts.find((item) => item.name === "scraper-output-karachi");

  if (!artifact) {
    const err = new Error("No downloadable XLSX artifact is available for this workflow run yet.");
    err.status = 404;
    throw err;
  }

  return artifact.id;
}

module.exports = async (req, res) => {
  if (req.method !== "GET") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }

  const session = requireAuth(req, res);
  if (!session) {
    return;
  }

  const query = parseQuery(req);
  const runId = String(query.get("runId") || "").trim();
  let artifactId = String(query.get("artifactId") || "").trim();

  if (!isPositiveInteger(runId)) {
    json(res, 400, { error: "runId is required." });
    return;
  }

  if (artifactId && !isPositiveInteger(artifactId)) {
    json(res, 400, { error: "artifactId must be numeric." });
    return;
  }

  const cfg = getGithubConfig();

  try {
    if (!artifactId) {
      artifactId = String(await resolveArtifactId(cfg, runId));
    }

    const zipBuffer = await fetchArtifactZip(cfg, artifactId);
    const xlsx = extractFirstXlsx(zipBuffer);

    res.statusCode = 200;
    res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    res.setHeader("Content-Disposition", `attachment; filename="${xlsx.name}"`);
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.end(xlsx.buffer);
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};
