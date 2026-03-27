const { getGithubConfig, githubRequest, json, readJsonBody, requireAuth } = require("./_lib/auth");

async function getRunXlsxMeta(cfg, runId, tokenOverride) {
  try {
    const data = await githubRequest(
      `/repos/${cfg.owner}/${cfg.repo}/actions/runs/${runId}/artifacts?per_page=100`,
      {},
      tokenOverride
    );

    const artifacts = (data.artifacts || []).filter((artifact) => !artifact.expired);
    const artifact = artifacts.find((item) => item.name === "scraper-xlsx-karachi");

    if (!artifact) {
      return {
        xlsx_available: false,
        xlsx_download_url: "",
        xlsx_artifact_name: ""
      };
    }

    return {
      xlsx_available: true,
      xlsx_download_url: `/api/download-run-xlsx?runId=${runId}&artifactId=${artifact.id}`,
      xlsx_artifact_name: artifact.name
    };
  } catch (_err) {
    return {
      xlsx_available: false,
      xlsx_download_url: "",
      xlsx_artifact_name: ""
    };
  }
}

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

    const runs = await Promise.all((data.workflow_runs || []).map(async (r) => {
      const xlsxMeta = r.status === "completed"
        ? await getRunXlsxMeta(cfg, r.id, tokenOverride)
        : {
            xlsx_available: false,
            xlsx_download_url: "",
            xlsx_artifact_name: ""
          };

      return {
        id: r.id,
        status: r.status,
        conclusion: r.conclusion,
        event: r.event,
        created_at: r.created_at,
        updated_at: r.updated_at,
        html_url: r.html_url,
        actor: r.actor ? r.actor.login : "",
        display_title: r.display_title,
        xlsx_available: xlsxMeta.xlsx_available,
        xlsx_download_url: xlsxMeta.xlsx_download_url,
        xlsx_artifact_name: xlsxMeta.xlsx_artifact_name
      };
    }));

    json(res, 200, { runs });
  } catch (err) {
    json(res, err.status || 500, { error: err.message });
  }
};
