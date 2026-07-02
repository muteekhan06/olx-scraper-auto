const assert = require("node:assert/strict");
const test = require("node:test");

const {
  buildGithubApiError,
  getGithubConfig,
  normalizeGithubToken
} = require("../api/_lib/auth");

test("normalizeGithubToken removes common paste artifacts", () => {
  assert.equal(normalizeGithubToken(' "github_pat_example" '), "github_pat_example");
  assert.equal(normalizeGithubToken("Bearer ghp_example"), "ghp_example");
  assert.equal(normalizeGithubToken("'ghp_example'"), "ghp_example");
});

test("getGithubConfig accepts GH_TOKEN fallback when GITHUB_PAT is absent", () => {
  const originalPat = process.env.GITHUB_PAT;
  const originalGhToken = process.env.GH_TOKEN;

  delete process.env.GITHUB_PAT;
  process.env.GH_TOKEN = '"github_pat_from_gh_token"';

  try {
    assert.equal(getGithubConfig().token, "github_pat_from_gh_token");
  } finally {
    if (originalPat === undefined) {
      delete process.env.GITHUB_PAT;
    } else {
      process.env.GITHUB_PAT = originalPat;
    }
    if (originalGhToken === undefined) {
      delete process.env.GH_TOKEN;
    } else {
      process.env.GH_TOKEN = originalGhToken;
    }
  }
});

test("buildGithubApiError maps bad credentials to an actionable message", async () => {
  const resp = new Response(JSON.stringify({ message: "Bad credentials" }), { status: 401 });

  const err = await buildGithubApiError(resp);

  assert.equal(err.status, 401);
  assert.match(err.message, /Update the GITHUB_PAT environment variable in Vercel/);
  assert.match(err.message, /Actions workflow permissions/);
});
