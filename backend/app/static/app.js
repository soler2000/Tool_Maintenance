const API_BASE = "/api";

const state = {
  token: localStorage.getItem("tm_auth_token") || "",
  username: localStorage.getItem("tm_username") || "",
  defaultUserId: localStorage.getItem("tm_user_id") || "",
  loading: false,
  data: {
    tools: [],
    maintenanceLogs: [],
    shotCounters: [],
    failureCodes: [],
    failureReports: [],
    actionItems: [],
  },
  activeTab: localStorage.getItem("tm_active_tab") || "tools",
};

const elements = {
  dashboard: document.getElementById("dashboard"),
  unauthenticatedNote: document.getElementById("unauthenticated-note"),
  loginForm: document.getElementById("login-form"),
  registerForm: document.getElementById("register-form"),
  logoutButton: document.getElementById("logout-button"),
  userSummary: document.getElementById("user-summary"),
  authForms: document.getElementById("auth-forms"),
  sessionUsername: document.getElementById("session-username"),
  sessionUserId: document.getElementById("session-user-id"),
  userIdForm: document.getElementById("user-id-form"),
  maintenancePerformedBy: document.getElementById("maintenance-performed-by"),
  shotCounterRecordedBy: document.getElementById("shot-counter-recorded-by"),
  failureReportReportedBy: document.getElementById("failure-report-reported-by"),
  actionAssignedTo: document.getElementById("action-assigned-to"),
  maintenanceTool: document.getElementById("maintenance-tool"),
  shotCounterTool: document.getElementById("shot-counter-tool"),
  failureReportTool: document.getElementById("failure-report-tool"),
  failureReportCode: document.getElementById("failure-report-code"),
  actionTool: document.getElementById("action-tool"),
  actionFailureReport: document.getElementById("action-failure-report"),
  toast: document.getElementById("toast"),
  toolTableWrapper: document.getElementById("tools-table-wrapper"),
  maintenanceTableWrapper: document.getElementById("maintenance-table-wrapper"),
  shotCounterTableWrapper: document.getElementById("shot-counters-table-wrapper"),
  failureCodesTableWrapper: document.getElementById("failure-codes-table-wrapper"),
  failureReportsTableWrapper: document.getElementById("failure-reports-table-wrapper"),
  actionsTableWrapper: document.getElementById("actions-table-wrapper"),
  createToolForm: document.getElementById("create-tool-form"),
  createMaintenanceForm: document.getElementById("create-maintenance-form"),
  createShotCounterForm: document.getElementById("create-shot-counter-form"),
  createFailureCodeForm: document.getElementById("create-failure-code-form"),
  createFailureReportForm: document.getElementById("create-failure-report-form"),
  createActionForm: document.getElementById("create-action-form"),
  refreshButtons: {
    tools: document.getElementById("refresh-tools"),
    maintenance: document.getElementById("refresh-maintenance"),
    shotCounters: document.getElementById("refresh-shot-counters"),
    failureCodes: document.getElementById("refresh-failure-codes"),
    failureReports: document.getElementById("refresh-failure-reports"),
    actions: document.getElementById("refresh-actions"),
  },
  tabButtons: document.querySelectorAll("[data-tab]"),
  tabPanels: document.querySelectorAll("[data-tab-panel]"),
  shotCounterIncrement: document.getElementById("shot-counter-increment"),
  shotCounterCurrentTotal: document.getElementById("shot-counter-current-total"),
  shotCounterProjectedTotal: document.getElementById("shot-counter-projected-total"),
  shotCounterLimit: document.getElementById("shot-counter-limit"),
};

const numericFields = new Set([
  "cavity_count",
  "duration_minutes",
  "shot_count",
  "initial_shot_count",
  "max_shot_count",
]);

function formatNumber(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "-";
  }
  return Number(value).toLocaleString();
}

function getToolById(toolId) {
  return state.data.tools.find((tool) => tool.id === toolId);
}

function getToolInitialShots(toolId) {
  const tool = getToolById(toolId);
  return tool?.initial_shot_count ?? 0;
}

function getToolMaxShots(toolId) {
  const tool = getToolById(toolId);
  return tool?.max_shot_count ?? null;
}

function getToolCurrentShotTotal(toolId) {
  const initial = getToolInitialShots(toolId);
  const counters = state.data.shotCounters.filter((entry) => entry.tool_id === toolId);
  if (!counters.length) {
    return initial;
  }
  return counters.reduce((highest, entry) => Math.max(highest, entry.shot_count ?? 0), initial);
}

function computeShotHistory() {
  if (!state.data.shotCounters.length) {
    return [];
  }
  const sorted = [...state.data.shotCounters].sort((a, b) => {
    const aTime = a.recorded_at ? new Date(a.recorded_at).getTime() : 0;
    const bTime = b.recorded_at ? new Date(b.recorded_at).getTime() : 0;
    return aTime - bTime;
  });
  const runningTotals = {};
  return sorted.map((entry) => {
    const previousTotal = runningTotals[entry.tool_id] ?? getToolInitialShots(entry.tool_id);
    const increment = entry.shot_count - previousTotal;
    runningTotals[entry.tool_id] = entry.shot_count;
    const maxShots = getToolMaxShots(entry.tool_id);
    const overLimit = typeof maxShots === "number" && entry.shot_count > maxShots;
    return {
      ...entry,
      increment,
      maxShots,
      overLimit,
    };
  });
}

function setActiveTab(tabId) {
  const buttons = Array.from(elements.tabButtons || []);
  const panels = Array.from(elements.tabPanels || []);
  if (!buttons.length || !panels.length) {
    return;
  }
  const validTab = buttons.some((button) => button.dataset.tab === tabId)
    ? tabId
    : buttons[0]?.dataset.tab;
  buttons.forEach((button) => {
    const isActive = button.dataset.tab === validTab;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", isActive ? "true" : "false");
    button.setAttribute("tabindex", isActive ? "0" : "-1");
  });
  panels.forEach((panel) => {
    const isActive = panel.dataset.tabPanel === validTab;
    panel.toggleAttribute("hidden", !isActive);
    panel.setAttribute("aria-hidden", isActive ? "false" : "true");
  });
  if (validTab) {
    state.activeTab = validTab;
    localStorage.setItem("tm_active_tab", validTab);
  }
}

function initTabs() {
  const buttons = Array.from(elements.tabButtons || []);
  if (!buttons.length) {
    return;
  }
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      setActiveTab(button.dataset.tab);
    });
  });
  setActiveTab(state.activeTab || buttons[0]?.dataset.tab || "tools");
}

function updateShotCounterPreview() {
  const toolSelect = elements.shotCounterTool;
  const incrementField = elements.shotCounterIncrement;
  const currentTotalField = elements.shotCounterCurrentTotal;
  const projectedTotalField = elements.shotCounterProjectedTotal;
  const limitField = elements.shotCounterLimit;

  if (!toolSelect || !incrementField) {
    return;
  }

  const toolId = toolSelect.value;
  const increment = Number(incrementField.value || 0);
  const safeIncrement = Number.isNaN(increment) || increment < 0 ? 0 : increment;
  const currentTotal = toolId ? getToolCurrentShotTotal(toolId) : 0;
  const projectedTotal = toolId ? currentTotal + safeIncrement : safeIncrement;

  if (currentTotalField) {
    currentTotalField.textContent = formatNumber(currentTotal);
  }
  if (projectedTotalField) {
    projectedTotalField.textContent = formatNumber(projectedTotal);
  }
  if (limitField) {
    if (!toolId) {
      limitField.textContent = "Select a tool to calculate remaining shots.";
      limitField.dataset.status = "";
    } else {
      const maxShots = getToolMaxShots(toolId);
      if (typeof maxShots === "number") {
        const difference = maxShots - projectedTotal;
        if (difference < 0) {
          limitField.textContent = `Projected total exceeds max by ${formatNumber(Math.abs(difference))} shots (limit ${formatNumber(
            maxShots,
          )}).`;
          limitField.dataset.status = "over";
        } else {
          limitField.textContent = `${formatNumber(difference)} shots remaining before max (${formatNumber(maxShots)}).`;
          limitField.dataset.status = "within";
        }
      } else {
        limitField.textContent = "No maximum shot count set for this tool.";
        limitField.dataset.status = "";
      }
    }
  }
}

function showToast(message, type = "success") {
  if (!elements.toast) return;
  elements.toast.textContent = message;
  elements.toast.className = type === "error" ? "show danger" : "show";
  setTimeout(() => {
    elements.toast.className = elements.toast.className.replace("show", "").trim();
  }, 3500);
}

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
}

async function api(path, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  let body = options.body;
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body,
  });
  if (response.status === 204) {
    return null;
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail || data?.message || response.statusText;
    throw new Error(message || "Request failed");
  }
  return data;
}

function updateAuthState() {
  const isAuthenticated = Boolean(state.token);
  if (isAuthenticated) {
    elements.dashboard.hidden = false;
    elements.unauthenticatedNote.hidden = true;
    elements.authForms.hidden = true;
    elements.userSummary.hidden = false;
    elements.sessionUsername.textContent = state.username || "-";
    elements.sessionUserId.textContent = state.defaultUserId || "not set";
  } else {
    elements.dashboard.hidden = true;
    elements.unauthenticatedNote.hidden = false;
    elements.authForms.hidden = false;
    elements.userSummary.hidden = true;
    elements.sessionUsername.textContent = "-";
    elements.sessionUserId.textContent = "not set";
  }
  applyDefaultUserId();
}

function setToken(token, username) {
  state.token = token;
  state.username = username || state.username || "";
  if (token) {
    localStorage.setItem("tm_auth_token", token);
  } else {
    localStorage.removeItem("tm_auth_token");
  }
  if (state.username) {
    localStorage.setItem("tm_username", state.username);
  } else {
    localStorage.removeItem("tm_username");
  }
  updateAuthState();
  if (token) {
    void loadDashboard();
  } else {
    clearTables();
  }
}

function applyDefaultUserId() {
  const value = state.defaultUserId;
  elements.sessionUserId.textContent = value || "not set";
  [
    elements.maintenancePerformedBy,
    elements.shotCounterRecordedBy,
    elements.failureReportReportedBy,
    elements.actionAssignedTo,
  ].forEach((input) => {
    if (!input) return;
    if (!input.value) {
      input.value = value;
    }
  });
}

function setDefaultUserId(userId) {
  state.defaultUserId = userId;
  if (userId) {
    localStorage.setItem("tm_user_id", userId);
  } else {
    localStorage.removeItem("tm_user_id");
  }
  applyDefaultUserId();
}

function clearTables() {
  elements.toolTableWrapper.innerHTML = "";
  elements.maintenanceTableWrapper.innerHTML = "";
  elements.shotCounterTableWrapper.innerHTML = "";
  elements.failureCodesTableWrapper.innerHTML = "";
  elements.failureReportsTableWrapper.innerHTML = "";
  elements.actionsTableWrapper.innerHTML = "";
  [
    elements.maintenanceTool,
    elements.shotCounterTool,
    elements.failureReportTool,
    elements.failureReportCode,
    elements.actionTool,
    elements.actionFailureReport,
  ].forEach((select) => {
    if (select) {
      select.innerHTML = "";
    }
  });
  updateShotCounterPreview();
}

function renderEmptyState(message) {
  return `<div class="empty-state">${message}</div>`;
}

function renderTools() {
  const tools = state.data.tools;
  if (!tools.length) {
    elements.toolTableWrapper.innerHTML = renderEmptyState("No tools have been recorded yet.");
    return;
  }
  const rows = tools
    .map((tool) => {
      const statusClass = `status-${tool.status}`;
      const currentShots = getToolCurrentShotTotal(tool.id);
      const maxShots = tool.max_shot_count ?? null;
      const initialShots = tool.initial_shot_count ?? 0;
      const hasMaxShots = typeof maxShots === "number" && maxShots > 0;
      const utilisation = hasMaxShots ? Math.round((currentShots / maxShots) * 100) : null;
      const overLimit = hasMaxShots && currentShots > maxShots;
      const utilisationLabel = utilisation !== null ? `${utilisation}%` : "-";
      return `
        <tr>
          <td><code>${tool.asset_number}</code></td>
          <td>${tool.name}</td>
          <td>${tool.location || "-"}</td>
          <td>
            <span class="status-indicator ${statusClass}${overLimit ? " status-over-limit" : ""}">
              <span class="status-dot"></span>
              ${tool.status}
            </span>
          </td>
          <td>${tool.cavity_count ?? "-"}</td>
          <td>${formatNumber(initialShots)}</td>
          <td>${formatNumber(maxShots)}</td>
          <td>
            <span class="shot-total${overLimit ? " over" : ""}">${formatNumber(currentShots)}</span>
          </td>
          <td>${utilisationLabel}</td>
          <td>${formatDateTime(tool.created_at)}</td>
        </tr>
      `;
    })
    .join("");
  elements.toolTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Asset #</th>
          <th>Name</th>
          <th>Location</th>
          <th>Status</th>
          <th>Cavities</th>
          <th>Initial shots</th>
          <th>Max shots</th>
          <th>Current shots</th>
          <th>Utilisation</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderMaintenance() {
  const logs = state.data.maintenanceLogs;
  if (!logs.length) {
    elements.maintenanceTableWrapper.innerHTML = renderEmptyState("No maintenance logs found.");
    return;
  }
  const rows = logs
    .map((log) => `
      <tr>
        <td><code>${log.tool_id}</code></td>
        <td><code>${log.performed_by}</code></td>
        <td>${formatDateTime(log.performed_at)}</td>
        <td>${log.duration_minutes ?? "-"}</td>
        <td>${log.follow_up_required ? "Yes" : "No"}</td>
        <td>${log.observations || "-"}</td>
      </tr>
    `)
    .join("");
  elements.maintenanceTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Tool id</th>
          <th>Performed by</th>
          <th>Performed at</th>
          <th>Duration</th>
          <th>Follow up</th>
          <th>Observations</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderShotCounters() {
  const counters = computeShotHistory();
  if (!counters.length) {
    elements.shotCounterTableWrapper.innerHTML = renderEmptyState("No shot counters recorded.");
    updateShotCounterPreview();
    return;
  }
  const rows = counters
    .map((entry) => {
      const tool = getToolById(entry.tool_id);
      const toolLabel = tool ? `${tool.name} (${tool.asset_number})` : entry.tool_id;
      const statusLabel = entry.overLimit ? "Exceeded max" : "Within max";
      const statusCell = typeof entry.maxShots === "number"
        ? `<span class="badge ${entry.overLimit ? "danger" : "neutral"}">${statusLabel}</span>`
        : "-";
      return `
        <tr${entry.overLimit ? " class=\"over-limit\"" : ""}>
          <td>${toolLabel}</td>
          <td>${formatNumber(entry.increment)}</td>
          <td>${formatNumber(entry.shot_count)}</td>
          <td>${formatNumber(entry.maxShots)}</td>
          <td>${entry.source}</td>
          <td><code>${entry.recorded_by || "-"}</code></td>
          <td>${formatDateTime(entry.recorded_at)}</td>
          <td>${statusCell}</td>
        </tr>
      `;
    })
    .join("");
  elements.shotCounterTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Tool</th>
          <th>Shots added</th>
          <th>Total shots</th>
          <th>Max shots</th>
          <th>Source</th>
          <th>Recorded by</th>
          <th>Recorded at</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
  updateShotCounterPreview();
}

function renderFailureCodes() {
  const codes = state.data.failureCodes;
  if (!codes.length) {
    elements.failureCodesTableWrapper.innerHTML = renderEmptyState("No failure codes defined.");
    return;
  }
  const rows = codes
    .map((code) => `
      <tr>
        <td><code>${code.code}</code></td>
        <td>${code.name}</td>
        <td>${code.description || "-"}</td>
        <td><span class="badge severity-${code.severity_default}">${code.severity_default}</span></td>
        <td>${code.active ? "Active" : "Inactive"}</td>
      </tr>
    `)
    .join("");
  elements.failureCodesTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Code</th>
          <th>Name</th>
          <th>Description</th>
          <th>Default severity</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderFailureReports() {
  const reports = state.data.failureReports;
  if (!reports.length) {
    elements.failureReportsTableWrapper.innerHTML = renderEmptyState("No failure reports captured.");
    return;
  }
  const rows = reports
    .map((report) => `
      <tr>
        <td><code>${report.tool_id}</code></td>
        <td><code>${report.reported_by}</code></td>
        <td>${report.failure_code_id ? `<code>${report.failure_code_id}</code>` : "-"}</td>
        <td><span class="badge severity-${report.severity}">${report.severity}</span></td>
        <td>${formatDateTime(report.occurred_at)}</td>
        <td>${report.description || "-"}</td>
      </tr>
    `)
    .join("");
  elements.failureReportsTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Tool id</th>
          <th>Reported by</th>
          <th>Failure code</th>
          <th>Severity</th>
          <th>Occurred at</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderActionItems() {
  const items = state.data.actionItems;
  if (!items.length) {
    elements.actionsTableWrapper.innerHTML = renderEmptyState("No action items assigned yet.");
    return;
  }
  const rows = items
    .map((item) => `
      <tr>
        <td>${item.title}</td>
        <td><span class="badge status-${item.status}">${item.status.replace("_", " ")}</span></td>
        <td><code>${item.tool_id}</code></td>
        <td>${item.failure_report_id ? `<code>${item.failure_report_id}</code>` : "-"}</td>
        <td><code>${item.assigned_to}</code></td>
        <td>${item.due_date ? formatDate(item.due_date) : "-"}</td>
      </tr>
    `)
    .join("");
  elements.actionsTableWrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th>Tool id</th>
          <th>Failure report</th>
          <th>Assignee</th>
          <th>Due date</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function populateSelect(selectElement, options, { includeEmpty = false, emptyLabel = "None" } = {}) {
  if (!selectElement) return;
  const currentValue = selectElement.value;
  selectElement.innerHTML = "";
  if (includeEmpty) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = emptyLabel;
    selectElement.appendChild(option);
  }
  options.forEach(({ value, label }) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    selectElement.appendChild(option);
  });
  if (currentValue) {
    selectElement.value = currentValue;
  }
}

function refreshSelections() {
  const toolOptions = state.data.tools.map((tool) => ({ value: tool.id, label: `${tool.name} (${tool.asset_number})` }));
  populateSelect(elements.maintenanceTool, toolOptions);
  populateSelect(elements.shotCounterTool, toolOptions);
  populateSelect(elements.failureReportTool, toolOptions);
  populateSelect(elements.actionTool, toolOptions);

  const failureCodeOptions = state.data.failureCodes.map((code) => ({ value: code.id, label: `${code.code} — ${code.name}` }));
  populateSelect(elements.failureReportCode, failureCodeOptions, { includeEmpty: true, emptyLabel: "None" });

  const failureReportOptions = state.data.failureReports.map((report) => ({ value: report.id, label: `${report.id.slice(0, 8)} – ${report.description?.slice(0, 40) || "Report"}` }));
  populateSelect(elements.actionFailureReport, failureReportOptions, { includeEmpty: true, emptyLabel: "None" });
  updateShotCounterPreview();
}

async function loadDashboard() {
  if (!state.token) return;
  try {
    state.loading = true;
    const [tools, maintenanceLogs, shotCounters, failureCodes, failureReports, actionItems] = await Promise.all([
      api("/tools"),
      api("/maintenance"),
      api("/shot-counters"),
      api("/failures/codes"),
      api("/failures/reports"),
      api("/actions"),
    ]);
    state.data = { tools, maintenanceLogs, shotCounters, failureCodes, failureReports, actionItems };
    renderTools();
    renderMaintenance();
    renderShotCounters();
    renderFailureCodes();
    renderFailureReports();
    renderActionItems();
    refreshSelections();
    applyDefaultUserId();
    updateShotCounterPreview();
    showToast("Dashboard updated");
  } catch (error) {
    console.error(error);
    showToast(error.message, "error");
  } finally {
    state.loading = false;
  }
}

function formDataToObject(form) {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

function sanitisePayload(payload) {
  const cleaned = {};
  Object.entries(payload).forEach(([key, value]) => {
    if (value === "") return;
    if (value === "true") {
      cleaned[key] = true;
    } else if (value === "false") {
      cleaned[key] = false;
    } else if (typeof value === "number") {
      cleaned[key] = value;
    } else if (typeof value === "string" && value.trim() !== "" && !Number.isNaN(Number(value)) && numericFields.has(key)) {
      cleaned[key] = Number(value);
    } else {
      cleaned[key] = value;
    }
  });
  return cleaned;
}

function attachEventListeners() {
  elements.loginForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = formDataToObject(elements.loginForm);
    try {
      const data = await api("/auth/token", { method: "POST", body: payload });
      setToken(data.access_token, payload.username);
      showToast("Signed in successfully");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.registerForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = formDataToObject(elements.registerForm);
    try {
      const data = await api("/auth/register", { method: "POST", body: payload });
      showToast(`User created. Id: ${data.id}`);
      setDefaultUserId(data.id);
      state.username = data.username;
      localStorage.setItem("tm_username", state.username);
      elements.registerForm.reset();
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.logoutButton?.addEventListener("click", () => {
    localStorage.removeItem("tm_auth_token");
    localStorage.removeItem("tm_username");
    state.username = "";
    setToken("", "");
    showToast("Signed out");
  });

  elements.userIdForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = formDataToObject(elements.userIdForm);
    setDefaultUserId(payload.user_id || "");
    showToast("Default user id saved");
  });

  elements.createToolForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = sanitisePayload(formDataToObject(elements.createToolForm));
    try {
      await api("/tools", { method: "POST", body: payload });
      elements.createToolForm.reset();
      await loadDashboard();
      showToast("Tool created");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.createMaintenanceForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = sanitisePayload(formDataToObject(elements.createMaintenanceForm));
    try {
      await api("/maintenance", { method: "POST", body: payload });
      elements.createMaintenanceForm.reset();
      applyDefaultUserId();
      await loadDashboard();
      showToast("Maintenance log recorded");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.createShotCounterForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formValues = formDataToObject(elements.createShotCounterForm);
    const toolId = formValues.tool_id;
    const increment = Number(formValues.shot_increment ?? formValues.shot_count ?? 0);
    if (!toolId) {
      showToast("Select a tool before logging shots", "error");
      return;
    }
    if (!Number.isFinite(increment) || increment <= 0) {
      showToast("Enter a shot increment greater than zero", "error");
      return;
    }
    const payload = sanitisePayload({
      tool_id: toolId,
      recorded_by: formValues.recorded_by,
      source: formValues.source,
      shot_count: getToolCurrentShotTotal(toolId) + increment,
    });
    try {
      await api("/shot-counters", { method: "POST", body: payload });
      elements.createShotCounterForm.reset();
      if (elements.shotCounterTool) {
        elements.shotCounterTool.value = toolId;
      }
      if (elements.shotCounterIncrement) {
        elements.shotCounterIncrement.value = "";
      }
      updateShotCounterPreview();
      applyDefaultUserId();
      await loadDashboard();
      showToast("Shot counter added");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.createFailureCodeForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = sanitisePayload(formDataToObject(elements.createFailureCodeForm));
    try {
      await api("/failures/codes", { method: "POST", body: payload });
      elements.createFailureCodeForm.reset();
      await loadDashboard();
      showToast("Failure code created");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.createFailureReportForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = sanitisePayload(formDataToObject(elements.createFailureReportForm));
    try {
      await api("/failures/reports", { method: "POST", body: payload });
      elements.createFailureReportForm.reset();
      applyDefaultUserId();
      await loadDashboard();
      showToast("Failure reported");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.createActionForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = sanitisePayload(formDataToObject(elements.createActionForm));
    try {
      await api("/actions", { method: "POST", body: payload });
      elements.createActionForm.reset();
      applyDefaultUserId();
      await loadDashboard();
      showToast("Action item created");
    } catch (error) {
      console.error(error);
      showToast(error.message, "error");
    }
  });

  elements.shotCounterTool?.addEventListener("change", () => {
    updateShotCounterPreview();
  });

  elements.shotCounterIncrement?.addEventListener("input", () => {
    updateShotCounterPreview();
  });

  elements.shotCounterIncrement?.addEventListener("change", () => {
    updateShotCounterPreview();
  });

  Object.entries(elements.refreshButtons).forEach(([key, button]) => {
    button?.addEventListener("click", async () => {
      try {
        switch (key) {
          case "tools":
            state.data.tools = await api("/tools");
            renderTools();
            refreshSelections();
            break;
          case "maintenance":
            state.data.maintenanceLogs = await api("/maintenance");
            renderMaintenance();
            break;
          case "shotCounters":
            state.data.shotCounters = await api("/shot-counters");
            renderShotCounters();
            updateShotCounterPreview();
            break;
          case "failureCodes":
            state.data.failureCodes = await api("/failures/codes");
            renderFailureCodes();
            refreshSelections();
            break;
          case "failureReports":
            state.data.failureReports = await api("/failures/reports");
            renderFailureReports();
            refreshSelections();
            break;
          case "actions":
            state.data.actionItems = await api("/actions");
            renderActionItems();
            break;
          default:
            break;
        }
        showToast("Section refreshed");
      } catch (error) {
        console.error(error);
        showToast(error.message, "error");
      }
    });
  });
}

initTabs();
attachEventListeners();
updateShotCounterPreview();
updateAuthState();
if (state.token) {
  void loadDashboard();
}
