const { getGithubConfig, githubRequest, json, requireAuth } = require("./_lib/auth");

module.exports = async (req, res) => {
  if (req.method !== "GET") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }

  const session = requireAuth(req, res);
  if (!session) {
    return;
  }

  const cfg = getGithubConfig();
  try {
    const data = await githubRequest(
      `/repos/${cfg.owner}/${cfg.repo}/actions/workflows/${cfg.workflowFile}/runs?per_page=10`
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

