/* ──────────────────────────────────────────────
   VulnLab — Shared Client Utilities
   ────────────────────────────────────────────── */

const API = "http://localhost:8001";

/* ── Token helpers ───────────────────────────── */
function getToken()          { return localStorage.getItem("vulnlab_token"); }
function setToken(tok)       { localStorage.setItem("vulnlab_token", tok); }
function getUsername()       { return localStorage.getItem("vulnlab_user"); }
function setUsername(u)      { localStorage.setItem("vulnlab_user", u); }
function clearAuth()         { localStorage.removeItem("vulnlab_token"); localStorage.removeItem("vulnlab_user"); }

/* ── Auth headers ─────────────────────────────── */
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken() || ""}`,
  };
}

/* ── Alert helpers ────────────────────────────── */
function showAlert(id, msg, type = "error") {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
}
function hideAlert(id) {
  const el = document.getElementById(id);
  if (el) el.className = "alert";
}

/* ── Nav: mark active link & show user ───────── */
function initNav() {
  const path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".topnav a[data-page]").forEach(a => {
    if (a.dataset.page === path) a.classList.add("active");
  });

  const userEl = document.getElementById("nav-user");
  const u = getUsername();
  if (userEl && u) userEl.textContent = `[${u}]`;

  // Logout button
  const logoutBtn = document.getElementById("btn-logout");
  if (logoutBtn) {
    if (u) {
      logoutBtn.style.display = "inline-flex";
      logoutBtn.addEventListener("click", () => {
        clearAuth();
        location.href = "login.html";
      });
    } else {
      logoutBtn.style.display = "none";
    }
  }
}

/* ── Redirect to login if not authenticated ─── */
function requireAuth() {
  if (!getToken()) {
    location.href = "login.html";
    return false;
  }
  return true;
}

/* ── Fetch vuln status and render badges ─────── */
async function renderVulnBar(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    const vulns = data.vulns || {};
    container.innerHTML = Object.entries(vulns).map(([k, v]) =>
      `<span class="badge ${v ? "badge-on" : "badge-off"}">${k}: ${v ? "ON ⚠" : "OFF ✓"}</span>`
    ).join("");
  } catch (_) {
    container.innerHTML = `<span class="badge badge-off">backend unreachable</span>`;
  }
}

document.addEventListener("DOMContentLoaded", initNav);
