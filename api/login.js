const {
  createSessionToken,
  getSessionSecret,
  json,
  readJsonBody,
  safeEqual,
  setSessionCookie,
  verifyPassword
} = require("./_lib/auth");

const attempts = new Map();

function getClientIp(req) {
  const xff = req.headers["x-forwarded-for"];
  if (typeof xff === "string" && xff.length > 0) {
    return xff.split(",")[0].trim();
  }
  return req.socket.remoteAddress || "unknown";
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }

  const secret = getSessionSecret();
  if (!secret) {
    json(res, 500, { error: "SESSION_SECRET is missing or too short." });
    return;
  }

  const adminUser = process.env.DASHBOARD_ADMIN_USERNAME || "";
  if (!adminUser) {
    json(res, 500, { error: "DASHBOARD_ADMIN_USERNAME is missing." });
    return;
  }

  const ip = getClientIp(req);
  const now = Date.now();
  const state = attempts.get(ip) || { count: 0, lockUntil: 0 };
  if (state.lockUntil > now) {
    json(res, 429, { error: "Too many attempts. Try again later." });
    return;
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (err) {
    json(res, 400, { error: err.message });
    return;
  }

  const username = String(body.username || "").trim();
  const password = String(body.password || "");

  const userOk = safeEqual(username, adminUser);
  const passOk = verifyPassword(password);

  if (!userOk || !passOk) {
    const nextCount = state.count + 1;
    const lockUntil = nextCount >= 5 ? now + 10 * 60 * 1000 : 0;
    attempts.set(ip, { count: nextCount, lockUntil });
    json(res, 401, { error: "Invalid credentials" });
    return;
  }

  attempts.delete(ip);

  const token = createSessionToken(adminUser, secret);
  setSessionCookie(res, token);
  json(res, 200, { ok: true, username: adminUser });
};

