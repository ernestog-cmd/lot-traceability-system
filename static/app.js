/* ================================================================
   LOT TRACEABILITY SYSTEM — app.js
   ================================================================ */

let allLots = [];
let currentUser = null;
let authToken = null;
const PAGE_SIZE = 7;
let activePage = 1;
let historyPage = 1;

/* ---- Theme ---- */
function initTheme() {
    const saved = localStorage.getItem("theme") || "dark";
    document.body.classList.toggle("light", saved === "light");
    updateThemeBtn();
}

function toggleTheme() {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    updateThemeBtn();
}

function updateThemeBtn() {
    const btn = document.getElementById("theme-toggle-btn");
    if (btn) btn.textContent = document.body.classList.contains("light") ? "Switch to Dark" : "Switch to Light";
}

initTheme();

/* ---- Auth ---- */
function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
    };
}

function getInitials(first, last) {
    return `${first[0]}${last[0]}`.toUpperCase();
}

document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        authToken = data.access_token;
        const meRes = await fetch("/auth/me", { headers: { "Authorization": `Bearer ${authToken}` } });
        currentUser = await meRes.json();
        document.getElementById("login-error").style.display = "none";
        showApp();
    } else {
        document.getElementById("login-error").style.display = "block";
    }
});

function showApp() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("main-app").style.display = "flex";

    const initials = getInitials(currentUser.first_name, currentUser.last_name);
    const avatarClass = `avatar-${currentUser.role}`;
    const fullName = `${currentUser.first_name} ${currentUser.last_name}`;

    const sidebarAvatar = document.getElementById("sidebar-avatar");
    sidebarAvatar.textContent = initials;
    sidebarAvatar.className = `avatar ${avatarClass}`;

    document.getElementById("sidebar-name").textContent = fullName;
    document.getElementById("sidebar-role").textContent = currentUser.role;

    const topbarAvatar = document.getElementById("topbar-avatar");
    topbarAvatar.textContent = initials;
    topbarAvatar.className = `avatar-sm ${avatarClass}`;

    document.getElementById("topbar-name").textContent = fullName;
    const badge = document.getElementById("topbar-role-badge");
    badge.textContent = currentUser.role;
    badge.className = `role-${currentUser.role}`;

    document.getElementById("settings-name").textContent = fullName;
    document.getElementById("settings-role").textContent = currentUser.role;

    buildSidebar();
    updateThemeBtn();
    loadAllData();
    showPage("dashboard");
}

function logout() {
    authToken = null;
    currentUser = null;
    allLots = [];
    document.getElementById("main-app").style.display = "none";
    document.getElementById("login-screen").style.display = "flex";
    document.getElementById("login-form").reset();
}

/* ---- Sidebar por rol ---- */
function buildSidebar() {
    const role = currentUser.role;
    const nav = document.getElementById("sidebar-nav");

    // Páginas visibles por rol
    const pages = {
        admin:         ["dashboard", "active-lots", "history", "audits", "reports", "admin"],
        engineer:      ["dashboard", "active-lots", "history", "audits", "reports"],
        manufacturing: ["dashboard", "active-lots", "history"],
        auditor:       ["dashboard", "active-lots", "history", "audits"],
    };

    const labels = {
        dashboard:    { icon: "⊞", label: "Dashboard" },
        "active-lots": { icon: "◈", label: "Active Lots" },
        history:      { icon: "◷", label: "History" },
        audits:       { icon: "✓", label: "Audits" },
        reports:      { icon: "▤", label: "Reports" },
        admin:        { icon: "👥", label: "Admin" },
    };

    const allowed = pages[role] || ["dashboard", "active-lots", "history"];

    nav.innerHTML = allowed.map(page => `
        <a class="nav-item" onclick="showPage('${page}')" data-page="${page}">
            <span class="nav-icon">${labels[page].icon}</span>
            <span>${labels[page].label}</span>
        </a>
    `).join("");
}

/* ---- Navigation ---- */
function showPage(page) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) pageEl.classList.add("active");

    const navEl = document.querySelector(`[data-page="${page}"]`);
    if (navEl) navEl.classList.add("active");

    const titles = {
        dashboard:    ["Dashboard",    "Pre-sterilization lot tracking"],
        "active-lots": ["Active Lots", "Lots currently in process"],
        history:      ["History",      "Lot tracking history"],
        audits:       ["Audits",       "Audit activity by inspector"],
        reports:      ["Reports",      "Daily and historical reports"],
        admin:        ["Admin",        "User management"],
        settings:     ["Settings",     "Application preferences"],
    };

    const [title, subtitle] = titles[page] || ["", ""];
    document.getElementById("page-title").textContent = title;
    document.getElementById("page-subtitle").textContent = subtitle;

    if (page === "active-lots") renderActiveLots();
    if (page === "history")     renderHistory();
    if (page === "audits")      renderAudits();
    if (page === "reports")     renderReports();
    if (page === "admin")       renderAdminUsers();
    if (page === "settings")    updateThemeBtn();
}

/* ---- Load All Data ---- */
async function loadAllData() {
    const response = await fetch("/lots/");
    allLots = await response.json();
    renderDashboard();
    buildActiveToolbar();
}

/* ---- Dashboard ---- */
function renderDashboard() {
    const statuses = allLots.map(l => l.status);
    document.getElementById("m-total").textContent    = allLots.length;
    document.getElementById("m-ready").textContent    = statuses.filter(s => s === "ready_for_audit").length;
    document.getElementById("m-audit").textContent    = statuses.filter(s => s === "in_audit_process").length;
    document.getElementById("m-released").textContent = statuses.filter(s => s === "released").length;
    document.getElementById("m-hold").textContent     = statuses.filter(s => ["hold","waiting_me_approval","waiting_qe_approval"].includes(s)).length;

    const recent = [...allLots]
        .filter(l => l.audited_at)
        .sort((a, b) => b.audited_at.localeCompare(a.audited_at))
        .slice(0, 5);

    const activityEl = document.getElementById("recent-activity");
    activityEl.innerHTML = recent.length === 0
        ? `<p style="padding:16px 20px;color:var(--text-muted);font-size:0.875rem;">No recent activity</p>`
        : recent.map(l => `
            <div class="activity-item">
                <div class="activity-dot" style="background:${statusColor(l.status)}"></div>
                <div>
                    <div class="activity-text">Lot <strong>${l.lot_id}</strong> — ${l.status.replace(/_/g," ")}</div>
                    <div class="activity-time">${l.audited_by ? `by ${l.audited_by.system_user}` : ""} · ${formatDate(l.audited_at)}</div>
                </div>
            </div>
        `).join("");

    const pending = allLots.filter(l => ["ready_for_audit","in_audit_process","waiting_me_approval","waiting_qe_approval"].includes(l.status));
    const pendingEl = document.getElementById("pending-actions");
    pendingEl.innerHTML = pending.length === 0
        ? `<p style="padding:16px 20px;color:var(--text-muted);font-size:0.875rem;">No pending actions</p>`
        : pending.slice(0, 5).map(l => `
            <div class="activity-item" onclick="openLotDetail(${l.batch_id})" style="cursor:pointer;">
                <div class="activity-dot" style="background:${statusColor(l.status)}"></div>
                <div>
                    <div class="activity-text">Lot <strong>${l.lot_id}</strong> — <span class="status status-${l.status}">${l.status.replace(/_/g," ")}</span></div>
                    <div class="activity-time">${l.part_number_code} · ${l.units} units</div>
                </div>
            </div>
        `).join("");
}

function statusColor(status) {
    const map = {
        ready_for_audit: "#94a3b8", in_audit_process: "#eab308",
        released: "#22c55e", hold: "#ef4444",
        waiting_me_approval: "#a855f7", waiting_qe_approval: "#3b82f6"
    };
    return map[status] || "#94a3b8";
}

function formatDate(iso) {
    if (!iso) return "-";
    return new Date(iso).toLocaleString();
}

/* ---- Active Lots ---- */
function buildActiveToolbar() {
    const container = document.getElementById("add-lot-btn-container");
    if (!container) return;
    container.innerHTML = "";

    const role = currentUser.role;
    if (role === "manufacturing" || role === "engineer") {
        container.innerHTML += `<button class="btn-primary" onclick="openCreateModal()">+ Add Lot</button>`;
    }
    if (role === "engineer") {
        container.innerHTML += `<button onclick="openFamilyModal()" style="margin-left:8px;">+ Family</button>`;
        container.innerHTML += `<button onclick="openPartNumberModal()" style="margin-left:8px;">+ Part Number</button>`;
        container.innerHTML += `<button onclick="openApproveModal()" style="margin-left:8px;">📋 Approvals</button>`;
    }
}

function getActiveLots() {
    const activeStatuses = ["ready_for_audit","in_audit_process","waiting_me_approval","waiting_qe_approval","hold"];
    const search = document.getElementById("search-active")?.value.toLowerCase() || "";
    const family = document.getElementById("filter-family")?.value || "";
    const status = document.getElementById("filter-status")?.value || "";

    return allLots.filter(l => {
        if (!activeStatuses.includes(l.status)) return false;
        if (search && !`${l.lot_id} ${l.part_number_code} ${l.part_number_description || ""}`.toLowerCase().includes(search)) return false;
        if (family && l.product_family !== family) return false;
        if (status && l.status !== status) return false;
        return true;
    });
}

function filterActiveLots() { activePage = 1; renderActiveLots(); }

function renderActiveLots() {
    const lots = getActiveLots();
    const start = (activePage - 1) * PAGE_SIZE;
    const paginated = lots.slice(start, start + PAGE_SIZE);
    const tbody = document.getElementById("active-lots-body");
    if (!tbody) return;

    tbody.innerHTML = paginated.map(lot => {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status.replace(/_/g," ")}</span>`;
        const actions = buildRowActions(lot);
        return `
            <tr onclick="openLotDetail(${lot.batch_id})">
                <td><strong>${lot.lot_id}</strong></td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family || "-"}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
                <td onclick="event.stopPropagation()">${actions}</td>
            </tr>
        `;
    }).join("");

    renderPagination("active-pagination", lots.length, activePage, (p) => { activePage = p; renderActiveLots(); });
    populateFamilyFilter();
}

function buildRowActions(lot) {
    const role = currentUser?.role;
    let actions = "";
    if (lot.status === "ready_for_audit" && role === "auditor")
        actions += `<button onclick="openAuditModal(${lot.batch_id})" style="padding:5px 12px;font-size:0.8rem;">Audit</button>`;
    if (lot.status === "in_audit_process" && role === "auditor")
        actions += `<button onclick="openDisposition(${lot.batch_id})" style="padding:5px 12px;font-size:0.8rem;" class="btn-release">Dispose</button>`;
    if (["hold","waiting_me_approval","waiting_qe_approval"].includes(lot.status) && (role === "engineer" || role === "manufacturing")) {
        let label = "Sign Return";
        if (lot.status === "waiting_me_approval") label = "Sign (ME)";
        else if (lot.status === "waiting_qe_approval") label = "Sign (QE)";
        actions += `<button onclick="openReturnModal(${lot.batch_id})" class="btn-sign" style="padding:5px 12px;font-size:0.8rem;">${label}</button>`;
    }
    return actions || "-";
}

function populateFamilyFilter() {
    const select = document.getElementById("filter-family");
    if (!select) return;
    const families = [...new Set(allLots.map(l => l.product_family).filter(Boolean))];
    const current = select.value;
    select.innerHTML = `<option value="">All Families</option>`;
    families.forEach(f => { select.innerHTML += `<option value="${f}" ${f === current ? "selected" : ""}>${f}</option>`; });
}

/* ---- History ---- */
function getHistoryLots() {
    const search   = document.getElementById("search-history")?.value.toLowerCase() || "";
    const status   = document.getElementById("filter-history-status")?.value || "";
    const dateFrom = document.getElementById("filter-date-from")?.value || "";
    const dateTo   = document.getElementById("filter-date-to")?.value || "";

    return allLots.filter(l => {
        if (!["released","hold"].includes(l.status)) return false;
        if (search && !`${l.lot_id} ${l.part_number_code} ${l.part_number_description || ""}`.toLowerCase().includes(search)) return false;
        if (status && l.status !== status) return false;
        if (dateFrom && l.audited_at && l.audited_at < dateFrom) return false;
        if (dateTo   && l.audited_at && l.audited_at > dateTo + "T23:59:59") return false;
        return true;
    }).sort((a, b) => (b.audited_at || "").localeCompare(a.audited_at || ""));
}

function filterHistory() { historyPage = 1; renderHistory(); }

function renderHistory() {
    const lots = getHistoryLots();
    const start = (historyPage - 1) * PAGE_SIZE;
    const paginated = lots.slice(start, start + PAGE_SIZE);
    const tbody = document.getElementById("history-body");
    if (!tbody) return;

    tbody.innerHTML = paginated.map(lot => {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status.replace(/_/g," ")}</span>`;
        return `
            <tr onclick="openLotDetail(${lot.batch_id})">
                <td><strong>${lot.lot_id}</strong></td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family || "-"}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
                <td>${lot.audited_at ? formatDate(lot.audited_at) : "-"}</td>
                <td>${lot.ncr_number || "-"}</td>
            </tr>
        `;
    }).join("");

    renderPagination("history-pagination", lots.length, historyPage, (p) => { historyPage = p; renderHistory(); });
}

/* ---- Audits ---- */
function renderAudits() {
    const audited = allLots
        .filter(l => l.audited_by)
        .sort((a, b) => (b.audited_at || "").localeCompare(a.audited_at || ""));

    const tbody = document.getElementById("audits-body");
    if (!tbody) return;

    tbody.innerHTML = audited.map(lot => `
        <tr onclick="openLotDetail(${lot.batch_id})">
            <td>${lot.audited_by.system_user}</td>
            <td><strong>${lot.lot_id}</strong></td>
            <td>${lot.part_number_code}</td>
            <td>${lot.part_number_description || "-"}</td>
            <td>${lot.audited_at ? formatDate(lot.audited_at) : "-"}</td>
            <td><span class="status status-${lot.status}">${lot.status.replace(/_/g," ")}</span></td>
            <td>${lot.ncr_number || "-"}</td>
        </tr>
    `).join("");
}

/* ---- Reports ---- */
function renderReports() {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("report-date").textContent = new Date().toLocaleDateString();

    const todayLots = allLots.filter(l => l.audited_at && l.audited_at.startsWith(today));
    document.getElementById("r-inspected").textContent = todayLots.length;
    document.getElementById("r-released").textContent  = todayLots.filter(l => l.status === "released").length;
    document.getElementById("r-hold").textContent      = todayLots.filter(l => l.status === "hold").length;
    document.getElementById("r-pending").textContent   = allLots.filter(l => ["ready_for_audit","in_audit_process"].includes(l.status)).length;

    const dailyBody = document.getElementById("daily-report-body");
    if (dailyBody) {
        dailyBody.innerHTML = todayLots.length > 0
            ? todayLots.map(l => `
                <tr>
                    <td>${l.lot_id}</td>
                    <td>${l.part_number_code}</td>
                    <td><span class="status status-${l.status}">${l.status.replace(/_/g," ")}</span></td>
                    <td>${l.audited_by ? l.audited_by.system_user : "-"}</td>
                    <td>${l.ncr_number || "-"}</td>
                </tr>
            `).join("")
            : `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:20px;">No lots inspected today</td></tr>`;
    }

    const pnMap = {};
    allLots.forEach(l => {
        const key = l.part_number_code;
        if (!pnMap[key]) pnMap[key] = { desc: l.part_number_description || "-", family: l.product_family || "-", total: 0, released: 0, hold: 0, pending: 0 };
        pnMap[key].total++;
        if (l.status === "released") pnMap[key].released++;
        else if (["hold","waiting_me_approval","waiting_qe_approval"].includes(l.status)) pnMap[key].hold++;
        else pnMap[key].pending++;
    });

    const pnBody = document.getElementById("pn-report-body");
    if (pnBody) {
        pnBody.innerHTML = Object.entries(pnMap).map(([code, data]) => `
            <tr>
                <td><strong>${code}</strong></td>
                <td>${data.desc}</td>
                <td>${data.family}</td>
                <td>${data.total}</td>
                <td style="color:var(--green)">${data.released}</td>
                <td style="color:var(--red)">${data.hold}</td>
                <td style="color:var(--yellow)">${data.pending}</td>
            </tr>
        `).join("");
    }
}

/* ---- Export ---- */
function exportHistory(format) {
    const lots = getHistoryLots();
    if (format === "csv") exportCSV(lots, "history");
    else exportPDF(lots, "History Report");
}

function exportReport(type, format) {
    let lots, title;
    if (type === "daily") {
        const today = new Date().toISOString().split("T")[0];
        lots  = allLots.filter(l => l.audited_at && l.audited_at.startsWith(today));
        title = `Daily Report — ${new Date().toLocaleDateString()}`;
    } else {
        lots  = allLots;
        title = "Historical by Part Number";
    }
    if (format === "csv") exportCSV(lots, type);
    else exportPDF(lots, title);
}

function exportCSV(lots, filename) {
    const headers = ["Lot ID","Part Number","Description","Family","Units","Status","Audited By","Audit Date","NCR"];
    const rows = lots.map(l => [
        l.lot_id, l.part_number_code, l.part_number_description || "", l.product_family || "",
        l.units, l.status, l.audited_by ? l.audited_by.system_user : "", l.audited_at || "", l.ncr_number || ""
    ]);
    const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

function exportPDF(lots, title) {
    const rows = lots.map(l => `
        <tr>
            <td>${l.lot_id}</td><td>${l.part_number_code}</td>
            <td>${l.part_number_description || "-"}</td><td>${l.product_family || "-"}</td>
            <td>${l.units}</td><td>${l.status.replace(/_/g," ")}</td>
            <td>${l.audited_by ? l.audited_by.system_user : "-"}</td>
            <td>${l.audited_at ? formatDate(l.audited_at) : "-"}</td>
            <td>${l.ncr_number || "-"}</td>
        </tr>
    `).join("");

    const html = `<html><head><style>
        body{font-family:Arial,sans-serif;font-size:12px;padding:20px;}
        h1{font-size:18px;margin-bottom:16px;}
        table{width:100%;border-collapse:collapse;}
        th{background:#374151;color:white;padding:8px;text-align:left;font-size:11px;}
        td{padding:7px 8px;border-bottom:1px solid #e2e8f0;}
    </style></head><body>
        <h1>${title}</h1>
        <p>Generated: ${new Date().toLocaleString()}</p>
        <table><thead><tr>
            <th>Lot ID</th><th>Part Number</th><th>Description</th><th>Family</th>
            <th>Units</th><th>Status</th><th>Audited By</th><th>Audit Date</th><th>NCR</th>
        </tr></thead><tbody>${rows}</tbody></table>
    </body></html>`;

    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
    win.print();
}

/* ---- Pagination ---- */
function renderPagination(containerId, total, current, onPage) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const totalPages = Math.ceil(total / PAGE_SIZE);
    if (totalPages <= 1) { container.innerHTML = ""; return; }

    let html = "";
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="page-btn ${i === current ? "active" : ""}" onclick="(${onPage.toString()})(${i})">${i}</button>`;
    }
    const showing = Math.min(current * PAGE_SIZE, total);
    const from    = (current - 1) * PAGE_SIZE + 1;
    container.innerHTML = `
        <span style="font-size:0.8rem;color:var(--text-muted);">Showing ${from}–${showing} of ${total}</span>
        ${html}
    `;
}

/* ---- Lot Detail Panel ---- */
function openLotDetail(batchId) {
    const lot = allLots.find(l => l.batch_id === batchId);
    if (!lot) return;

    document.getElementById("detail-lot-id").textContent = lot.lot_id;
    const statusBadge = document.getElementById("detail-status-badge");
    statusBadge.textContent = lot.status.replace(/_/g, " ");
    statusBadge.className = `status status-${lot.status}`;

    document.getElementById("d-pn").textContent       = lot.part_number_code;
    document.getElementById("d-desc").textContent     = lot.part_number_description || "-";
    document.getElementById("d-family").textContent   = lot.product_family || "-";
    document.getElementById("d-units").textContent    = lot.units;
    document.getElementById("d-mfg-date").textContent = lot.manufacturing_date || "-";
    document.getElementById("d-status").textContent   = lot.status.replace(/_/g, " ");

    if (lot.audited_by) {
        document.getElementById("d-auditor").textContent      = lot.audited_by.system_user;
        document.getElementById("d-auditor-name").textContent = `${lot.audited_by.first_name} ${lot.audited_by.last_name}`;
        document.getElementById("d-audit-date").textContent   = formatDate(lot.audited_at);
        document.getElementById("d-ncr").textContent          = lot.ncr_number || "-";
        document.getElementById("d-audit-section").style.display = "block";
    } else {
        document.getElementById("d-audit-section").style.display = "none";
    }

    const holdSection = document.getElementById("d-hold-section");
    if (["hold","waiting_me_approval","waiting_qe_approval"].includes(lot.status)) {
        holdSection.style.display = "block";
        document.getElementById("d-me-sign").textContent = lot.me_approved_by || "Pending";
        document.getElementById("d-qe-sign").textContent = lot.qe_approved_by || "Pending";
    } else {
        holdSection.style.display = "none";
    }

    document.getElementById("d-actions").innerHTML = buildDetailActions(lot);
    document.getElementById("lot-detail-overlay").style.display = "block";
    document.getElementById("lot-detail-panel").classList.add("open");
}

function buildDetailActions(lot) {
    const role = currentUser?.role;
    let html = "";
    if (lot.status === "ready_for_audit" && role === "auditor")
        html += `<button class="btn-primary" onclick="openAuditModal(${lot.batch_id}); closeLotDetail()">Start Audit</button>`;
    if (lot.status === "in_audit_process" && role === "auditor")
        html += `<button class="btn-release" onclick="openDisposition(${lot.batch_id}); closeLotDetail()">Disposition</button>`;
    if (["hold","waiting_me_approval","waiting_qe_approval"].includes(lot.status) && (role === "engineer" || role === "manufacturing"))
        html += `<button class="btn-sign" onclick="openReturnModal(${lot.batch_id}); closeLotDetail()">Sign Return from Hold</button>`;
    return html;
}

function closeLotDetail() {
    document.getElementById("lot-detail-overlay").style.display = "none";
    document.getElementById("lot-detail-panel").classList.remove("open");
}

/* ---- Admin ---- */
async function renderAdminUsers() {
    const response = await fetch("/users/", { headers: authHeaders() });
    const users = await response.json();

    let html = `
        <table class="users-table">
            <thead><tr>
                <th>Username</th><th>Name</th><th>Role</th><th>Status</th><th>Actions</th>
            </tr></thead><tbody>
    `;

    for (const user of users) {
        const isActive = user.is_active === "true";
        const statusBadge = isActive
            ? `<span class="badge-active">Active</span>`
            : `<span class="badge-inactive">Inactive</span>`;
        const roleOptions = ["admin","manufacturing","engineer","auditor"]
            .map(r => `<option value="${r}" ${r === user.role ? "selected" : ""}>${r}</option>`).join("");

        html += `
            <tr>
                <td>${user.username}</td>
                <td>${user.first_name} ${user.last_name}</td>
                <td>
                    <select id="role-${user.username}" class="role-select">${roleOptions}</select>
                    <button onclick="changeRole('${user.username}')" style="padding:4px 10px;font-size:0.8rem;margin-left:6px;">Save</button>
                </td>
                <td>${statusBadge}</td>
                <td>
                    <button onclick="toggleUser('${user.username}')" class="${isActive ? "btn-hold" : "btn-release"}" style="padding:5px 14px;font-size:0.8rem;">
                        ${isActive ? "Deactivate" : "Activate"}
                    </button>
                </td>
            </tr>
        `;
    }

    html += `</tbody></table>`;
    document.getElementById("manage-users-list").innerHTML = html;
}

async function toggleUser(username) {
    const res = await fetch(`/users/${username}/toggle-active`, { method: "PATCH", headers: authHeaders() });
    if (res.ok) renderAdminUsers();
    else { const e = await res.json(); alert(`Error: ${e.detail}`); }
}

async function changeRole(username) {
    const role = document.getElementById(`role-${username}`).value;
    const res  = await fetch(`/users/${username}/role`, { method: "PATCH", headers: authHeaders(), body: JSON.stringify({ role }) });
    if (res.ok) { alert("Role updated"); renderAdminUsers(); }
    else { const e = await res.json(); alert(`Error: ${e.detail}`); }
}

/* ---- Product Family modal ---- */
function openFamilyModal()  { document.getElementById("family-modal").style.display = "flex"; }
function closeFamilyModal() { document.getElementById("family-modal").style.display = "none"; document.getElementById("family-form").reset(); }

document.getElementById("family-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = { name: document.getElementById("family-name").value };
    const res  = await fetch("/product-families/", { method: "POST", headers: authHeaders(), body: JSON.stringify(data) });
    if (res.ok) { closeFamilyModal(); alert(`Family '${data.name}' proposed. Pending QE approval.`); }
    else { const err = await res.json(); alert(`Error: ${err.detail}`); }
});

/* ---- Part Number modal ---- */
async function openPartNumberModal() {
    const res     = await fetch("/product-families/active");
    const families = await res.json();
    const select  = document.getElementById("pn-family");
    select.innerHTML = `<option value="">-- Select Family --</option>`;
    families.forEach(f => { select.innerHTML += `<option value="${f.name}">${f.name}</option>`; });
    document.getElementById("part-number-modal").style.display = "flex";
}
function closePartNumberModal() { document.getElementById("part-number-modal").style.display = "none"; document.getElementById("part-number-form").reset(); }

document.getElementById("part-number-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = { code: document.getElementById("pn-code").value, description: document.getElementById("pn-description").value, family_name: document.getElementById("pn-family").value };
    const res  = await fetch("/part-numbers/", { method: "POST", headers: authHeaders(), body: JSON.stringify(data) });
    if (res.ok) { closePartNumberModal(); alert(`Part number '${data.code}' proposed. Pending QE approval.`); }
    else { const err = await res.json(); alert(`Error: ${err.detail}`); }
});

/* ---- Create Lot modal ---- */
async function openCreateModal() {
    const res        = await fetch("/part-numbers/active");
    const partNumbers = await res.json();
    const select     = document.getElementById("part_number_code");
    select.innerHTML = `<option value="">-- Select Part Number --</option>`;
    partNumbers.forEach(pn => { select.innerHTML += `<option value="${pn.code}">${pn.code} — ${pn.description}</option>`; });
    document.getElementById("create-modal").style.display = "flex";
}
function closeCreateModal() { document.getElementById("create-modal").style.display = "none"; document.getElementById("create-lot-form").reset(); }

document.getElementById("create-lot-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const newLot = {
        lot_id: document.getElementById("lot_id").value,
        part_number_code: document.getElementById("part_number_code").value,
        units: parseInt(document.getElementById("units").value),
        manufacturing_date: document.getElementById("manufacturing_date").value,
        status: "ready_for_audit"
    };
    const res = await fetch("/lots/", { method: "POST", headers: authHeaders(), body: JSON.stringify(newLot) });
    if (res.ok) {
        const created = await res.json();
        closeCreateModal();
        await loadAllData();
        renderActiveLots();
        alert(`Lot ${created.lot_id} created successfully`);
    } else { const err = await res.json(); alert(`Error: ${err.detail}`); }
});

/* ---- Audit modal ---- */
function openAuditModal(batchId) { document.getElementById("audit-lot-form").dataset.batchId = batchId; document.getElementById("audit-modal").style.display = "flex"; }
function cancelAudit()           { document.getElementById("audit-modal").style.display = "none"; document.getElementById("audit-lot-form").reset(); }

document.getElementById("audit-lot-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const batchId = this.dataset.batchId;
    const body    = { username: document.getElementById("audit-username").value, password: document.getElementById("audit-password").value };
    const res     = await fetch(`/lots/${batchId}/audit`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (res.ok) { cancelAudit(); await loadAllData(); renderActiveLots(); alert("Audit process started successfully"); }
    else { const err = await res.json(); alert(`Error: ${err.detail}`); }
});

/* ---- Disposition modal ---- */
let dispositionBatchId = null;

function openDisposition(batchId) {
    const lot = allLots.find(l => l.batch_id === batchId);
    if (!lot) return;
    dispositionBatchId = batchId;
    document.getElementById("disp-lot-id").textContent      = lot.lot_id;
    document.getElementById("disp-part-number").textContent = lot.part_number_code;
    document.getElementById("disp-description").textContent = lot.part_number_description || "-";
    document.getElementById("disp-family").textContent      = lot.product_family || "-";
    document.getElementById("disp-units").textContent       = lot.units;
    if (lot.audited_by) {
        document.getElementById("disp-auditor-name").textContent = `${lot.audited_by.first_name} ${lot.audited_by.last_name}`;
        document.getElementById("disp-auditor-user").textContent = lot.audited_by.system_user;
    }
    document.getElementById("disp-audited-at").textContent = formatDate(lot.audited_at);
    document.getElementById("ncr-section").style.display   = "none";
    document.getElementById("confirm-hold-btn").style.display = "none";
    document.getElementById("ncr-number").value            = "";
    document.getElementById("disposition-modal").style.display = "flex";
}

function showNcrField() {
    document.getElementById("ncr-section").style.display     = "block";
    document.getElementById("confirm-hold-btn").style.display = "inline-block";
}

function closeDisposition() { document.getElementById("disposition-modal").style.display = "none"; dispositionBatchId = null; }

async function submitDisposition(decision) {
    const body = { decision };
    if (decision === "hold") {
        const ncr = document.getElementById("ncr-number").value.trim();
        if (!ncr) { alert("NCR number is required to place a lot on hold"); return; }
        body.ncr_number = ncr;
    }
    const res = await fetch(`/lots/${dispositionBatchId}/disposition`, { method: "PATCH", headers: authHeaders(), body: JSON.stringify(body) });
    if (res.ok) { closeDisposition(); await loadAllData(); renderActiveLots(); alert(`Lot dispositioned as ${decision}`); }
    else { const err = await res.json(); alert(`Error: ${err.detail}`); }
}

/* ---- Return from Hold modal ---- */
let returnBatchId = null;

function openReturnModal(batchId) {
    const lot = allLots.find(l => l.batch_id === batchId);
    if (!lot) return;
    returnBatchId = batchId;
    document.getElementById("return-lot-info").textContent    = `Lot ${lot.lot_id} — NCR: ${lot.ncr_number || "-"}`;
    let pending = "Requires both Manufacturing and QE Engineer signatures";
    if (lot.status === "waiting_me_approval") pending = "Waiting for Manufacturing signature";
    else if (lot.status === "waiting_qe_approval") pending = "Waiting for QE Engineer signature";
    document.getElementById("return-pending-info").textContent = pending;
    document.getElementById("return-modal").style.display      = "flex";
}

function closeReturnModal() { document.getElementById("return-modal").style.display = "none"; document.getElementById("return-form").reset(); returnBatchId = null; }

document.getElementById("return-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const body = { username: document.getElementById("return-username").value, password: document.getElementById("return-password").value };
    const res  = await fetch(`/lots/${returnBatchId}/return-from-hold`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (res.ok) {
        const result = await res.json();
        closeReturnModal();
        await loadAllData();
        renderActiveLots();
        alert(result.status === "ready_for_audit"
            ? "Both signatures received. Lot returned to Ready for Audit."
            : "Signature recorded. Waiting for the second signature.");
    } else { const err = await res.json(); alert(`Error: ${err.detail}`); }
});

/* ---- Pending Approvals modal ---- */
async function openApproveModal() {
    const [famRes, pnRes] = await Promise.all([fetch("/product-families/"), fetch("/part-numbers/")]);
    const families    = await famRes.json();
    const partNumbers = await pnRes.json();
    const pendingFam  = families.filter(f => f.status === "pending_qe_approval");
    const pendingPN   = partNumbers.filter(p => p.status === "pending_qe_approval");

    let html = "";
    if (pendingFam.length === 0 && pendingPN.length === 0) html = `<p style="color:var(--text-muted);padding:8px 0;">No pending approvals.</p>`;
    if (pendingFam.length > 0) {
        html += "<h3 style='margin-bottom:8px;'>Product Families</h3>";
        pendingFam.forEach(f => { html += `<div class="approve-item"><span>${f.name} — proposed by ${f.proposed_by}</span><button onclick="approveFamily('${f.name}')">Approve</button></div>`; });
    }
    if (pendingPN.length > 0) {
        html += "<h3 style='margin:16px 0 8px;'>Part Numbers</h3>";
        pendingPN.forEach(p => { html += `<div class="approve-item"><span>${p.code} — ${p.description} — proposed by ${p.proposed_by}</span><button onclick="approvePN('${p.code}')">Approve</button></div>`; });
    }
    document.getElementById("approve-list").innerHTML = html;
    document.getElementById("approve-modal").style.display = "flex";
}

function closeApproveModal() { document.getElementById("approve-modal").style.display = "none"; }

async function approveFamily(name) {
    const res = await fetch(`/product-families/${name}/approve`, { method: "PATCH", headers: authHeaders() });
    if (res.ok) { alert(`Family '${name}' approved`); openApproveModal(); }
    else { const e = await res.json(); alert(`Error: ${e.detail}`); }
}

async function approvePN(code) {
    const res = await fetch(`/part-numbers/${code}/approve`, { method: "PATCH", headers: authHeaders() });
    if (res.ok) { alert(`Part number '${code}' approved`); openApproveModal(); }
    else { const e = await res.json(); alert(`Error: ${e.detail}`); }
}

/* ---- Create User modal ---- */
function openUserModal()  { document.getElementById("user-modal").style.display = "flex"; }
function closeUserModal() { document.getElementById("user-modal").style.display = "none"; document.getElementById("user-form").reset(); }

document.getElementById("user-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = {
        username:   document.getElementById("user-username").value,
        password:   document.getElementById("user-password").value,
        first_name: document.getElementById("user-firstname").value,
        last_name:  document.getElementById("user-lastname").value,
        role:       document.getElementById("user-role").value
    };
    const res = await fetch("/users/", { method: "POST", headers: authHeaders(), body: JSON.stringify(data) });
    if (res.ok) { closeUserModal(); alert(`User '${data.username}' created`); renderAdminUsers(); }
    else { const e = await res.json(); alert(`Error: ${e.detail}`); }
});