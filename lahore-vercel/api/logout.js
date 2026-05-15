const { clearSessionCookie, json } = require("./_lib/auth");

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }
  clearSessionCookie(res);
  json(res, 200, { ok: true });
};

