const crypto = require("crypto");

const COOKIE_NAME = "olx_admin_session";

function json(res, statusCode, payload) {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.end(JSON.stringify(payload));
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 1024 * 1024) {
        reject(new Error("Payload too large"));
      }
    });
    req.on("end", () => {
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(new Error("Invalid JSON body"));
      }
    });
    req.on("error", (err) => reject(err));
  });
}

function parseCookies(req) {
  const cookieHeader = req.headers.cookie || "";
  const out = {};
  cookieHeader.split(";").forEach((part) => {
    const idx = part.indexOf("=");
    if (idx > -1) {
      const key = part.slice(0, idx).trim();
      const value = part.slice(idx + 1).trim();
      out[key] = decodeURIComponent(value);
    }
  });
  return out;
}

function base64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function sign(payloadB64, secret) {
  return crypto.createHmac("sha256", secret).update(payloadB64).digest("base64url");
}

function createSessionToken(username, secret, ttlSeconds = 8 * 60 * 60) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    u: username,
    iat: now,
    exp: now + ttlSeconds
  };
  const payloadB64 = base64url(JSON.stringify(payload));
  const signature = sign(payloadB64, secret);
  return `${payloadB64}.${signature}`;
}

function verifySessionToken(token, secret) {
  if (!token || typeof token !== "string") {
    return null;
  }
  const [payloadB64, signature] = token.split(".");
  if (!payloadB64 || !signature) {
    return null;
  }
  const expected = sign(payloadB64, secret);
  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return null;
  }
  try {
    const payload = JSON.parse(Buffer.from(payloadB64, "base64url").toString("utf-8"));
    const now = Math.floor(Date.now() / 1000);
    if (!payload.exp || payload.exp < now) {
      return null;
    }
    return payload;
  } catch (_err) {
    return null;
  }
}

function getSessionSecret() {
  const secret = process.env.SESSION_SECRET || "";
  if (!secret || secret.length < 32) {
    return null;
  }
  return secret;
}

function setSessionCookie(res, token, maxAgeSeconds = 8 * 60 * 60) {
  const parts = [
    `${COOKIE_NAME}=${encodeURIComponent(token)}`,
    "HttpOnly",
    "Path=/",
    "Secure",
    "SameSite=Strict",
    `Max-Age=${maxAgeSeconds}`
  ];
  res.setHeader("Set-Cookie", parts.join("; "));
}

function clearSessionCookie(res) {
  res.setHeader(
    "Set-Cookie",
    `${COOKIE_NAME}=; HttpOnly; Path=/; Secure; SameSite=Strict; Max-Age=0`
  );
}

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") {
    return false;
  }
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) {
    return false;
  }
  return crypto.timingSafeEqual(ab, bb);
}

function verifyPassword(inputPassword) {
  const adminPassword = process.env.DASHBOARD_ADMIN_PASSWORD || "";
  const salt = process.env.DASHBOARD_ADMIN_SALT || "";
  const hash = process.env.DASHBOARD_ADMIN_PASSWORD_HASH || "";

  if (hash && salt) {
    const derived = crypto.pbkdf2Sync(inputPassword, salt, 120000, 32, "sha256").toString("hex");
    return safeEqual(derived, hash);
  }

  return safeEqual(inputPassword, adminPassword);
}

function requireAuth(req, res) {
  const secret = getSessionSecret();
  if (!secret) {
    json(res, 500, { error: "SESSION_SECRET is missing or too short." });
    return null;
  }
  const cookies = parseCookies(req);
  const payload = verifySessionToken(cookies[COOKIE_NAME], secret);
  if (!payload) {
    json(res, 401, { error: "Unauthorized" });
    return null;
  }
  return payload;
}

function getGithubConfig() {
  const owner = process.env.GITHUB_OWNER || "muteekhan06";
  const repo = process.env.GITHUB_REPO || "olx-scraper-auto";
  const token = process.env.GITHUB_PAT || "";
  const workflowFile = "karachi_daily_scrape.yml";
  const ref = process.env.KARACHI_WORKFLOW_REF || "main";
  return { owner, repo, token, workflowFile, ref };
}

async function githubRequest(path, options = {}) {
  const cfg = getGithubConfig();
  if (!cfg.token) {
    const err = new Error("GITHUB_PAT is missing.");
    err.status = 500;
    throw err;
  }
  const resp = await fetch(`https://api.github.com${path}`, {
    method: options.method || "GET",
    headers: {
      Authorization: `Bearer ${cfg.token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json"
    },
    body: options.body ? JSON.stringify(options.body) : undefined
  });

  if (!resp.ok) {
    const text = await resp.text();
    const err = new Error(`GitHub API failed (${resp.status}): ${text}`);
    err.status = resp.status;
    throw err;
  }

  if (resp.status === 204) {
    return null;
  }

  return resp.json();
}

module.exports = {
  COOKIE_NAME,
  clearSessionCookie,
  createSessionToken,
  getGithubConfig,
  getSessionSecret,
  githubRequest,
  json,
  parseCookies,
  readJsonBody,
  requireAuth,
  safeEqual,
  setSessionCookie,
  verifyPassword
};
