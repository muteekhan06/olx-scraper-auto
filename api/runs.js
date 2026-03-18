const { getGithubConfig, githubRequest, json, readJsonBody, requireAuth } = require("./_lib/auth");

module.exports = async (req, res) => {
  if (req.method !== "GET" && req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }

  const session = requireAuth(req, res);
  if (!session) {
    return;
  }

  let tokenOverride = "";
  if (req.method === "POST") {
    try {
      const body = await readJsonBody(req);
      tokenOverride = String(body.githubToken || "").trim();
    } catch (err) {
      json(res, 400, { error: err.message });
      return;
    }
  }

  const cfg = getGithubConfig(tokenOverride);
  try {
    const data = await githubRequest(
      `/repos/${cfg.owner}/${cfg.repo}/actions/workflows/${cfg.workflowFile}/runs?per_page=10`,
      {},
      tokenOverride
    );

    const runs = (data.workflow_runs || []).map((r) => ({
      id: r.id,
      status: r.status,
      conclusion: r.conclusion,
      event: r.event,
      created_at: r.created_at,
      updated_at: r.updated_at,
      html_url: r.html_url,
      actor: r.actor ? r.actor.login : "",
      display_title: r.display_title
    }));

    json(res, 200, { runs });
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};
