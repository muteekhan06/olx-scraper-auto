const { getGithubConfig, json, requireAuth } = require("./_lib/auth");
const { KARACHI_AREAS } = require("./_lib/karachi");

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
  json(res, 200, {
    authenticated: true,
    username: session.u,
    workflow: cfg.workflowFile,
    ref: cfg.ref,
    karachiAreas: KARACHI_AREAS
  });
};

