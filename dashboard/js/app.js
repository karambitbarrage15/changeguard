/**
 * ChangeGuard Dashboard Main App Controller
 */

// Service Endpoint Configs (fallback to relative if behind reverse proxy)
window.CONFIG = {
  TELEMETRY_URL: "http://localhost:8000",
  RISK_ENGINE_URL: "http://localhost:8001",
  MCP_SERVER_URL: "http://localhost:8002",
  SRE_AGENT_URL: "http://localhost:8003",
  RAG_ENGINE_URL: "http://localhost:8004"
};

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initServiceHealthCheck();
  loadPlaybooks();
});

function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

async function checkHealth(url) {
  try {
    const res = await fetch(`${url}/health`, { method: "GET" });
    return res.ok;
  } catch (e) {
    return false;
  }
}

async function initServiceHealthCheck() {
  const dots = {
    dotTelemetry: window.CONFIG.TELEMETRY_URL,
    dotRisk: window.CONFIG.RISK_ENGINE_URL,
    dotMcp: window.CONFIG.MCP_SERVER_URL,
    dotAgent: window.CONFIG.SRE_AGENT_URL,
    dotRag: window.CONFIG.RAG_ENGINE_URL
  };

  async function updateHealth() {
    let allHealthy = true;
    for (const [dotId, url] of Object.entries(dots)) {
      const el = document.getElementById(dotId);
      if (!el) continue;
      const isUp = await checkHealth(url);
      if (isUp) {
        el.className = "dot healthy";
      } else {
        el.className = "dot critical";
        allHealthy = false;
      }
    }

    const pill = document.getElementById("globalStatusPill");
    const text = document.getElementById("globalStatusText");
    if (!pill || !text) return;

    if (window.isSystemDegraded) {
      pill.className = "status-pill status-degraded";
      text.innerText = "INCIDENT DEGRADATION";
    } else if (allHealthy) {
      pill.className = "status-pill status-healthy";
      text.innerText = "ALL SYSTEMS NORMAL";
    } else {
      pill.className = "status-pill status-healthy";
      text.innerText = "SYSTEM ACTIVE";
    }
  }

  updateHealth();
  setInterval(updateHealth, 5000);
}

async function loadPlaybooks() {
  const grid = document.getElementById("kbGrid");
  if (!grid) return;

  try {
    const res = await fetch(`${window.CONFIG.RAG_ENGINE_URL}/rag/postmortems`);
    if (res.ok) {
      const data = await res.json();
      grid.innerHTML = "";
      data.postmortems.forEach(doc => {
        const card = document.createElement("div");
        card.className = "kb-card";
        card.innerHTML = `
          <div class="kb-header">
            <div class="kb-title">${doc.title}</div>
            <span class="badge ${doc.severity === 'P1' ? 'critical-badge' : 'warning-badge'}">${doc.severity}</span>
          </div>
          <div class="kb-snippet"><strong>Root Cause:</strong> ${doc.root_cause}</div>
        `;
        grid.appendChild(card);
      });
    }
  } catch (e) {
    grid.innerHTML = `<div class="empty-state">Knowledge base engine connecting...</div>`;
  }
}
