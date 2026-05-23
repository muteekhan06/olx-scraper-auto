const { getGithubConfig, githubRequest, json, readJsonBody, requireAuth } = require("./_lib/auth");

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

  const runId = String(body.runId || "").trim();
  if (!runId || !/^\d+$/.test(runId)) {
    json(res, 400, { error: "Invalid run ID." });
    return;
  }

  const githubToken = String(body.githubToken || "").trim();
  const cfg = getGithubConfig(githubToken);

  try {
    await githubRequest(
      `/repos/${cfg.owner}/${cfg.repo}/actions/runs/${runId}/cancel`,
      { method: "POST" },
      githubToken
    );

    json(res, 200, { ok: true, message: "Workflow run cancelled successfully." });
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};
