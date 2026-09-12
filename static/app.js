let currentLots = [];
let historyExpanded = false;
let currentUser = null;
let authToken = null;

/* ---- Auth ---- */
function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
    };
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

        const meResponse = await fetch("/auth/me", {
            headers: { "Authorization": `Bearer ${authToken}` }
        });
        currentUser = await meResponse.json();

        document.getElementById("login-error").style.display = "none";
        showApp();
    } else {
        document.getElementById("login-error").style.display = "block";
    }
});

function showApp() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("main-app").style.display = "block";

    document.getElementById("user-name").textContent =
        `${currentUser.first_name} ${currentUser.last_name}`;
    document.getElementById("user-role-badge").textContent = currentUser.role;

    buildToolbar();
    loadLots();
}

function logout() {
    authToken = null;
    currentUser = null;
    currentLots = [];
    document.getElementById("main-app").style.display = "none";
    document.getElementById("login-screen").style.display = "flex";
    document.getElementById("login-form").reset();
}

function buildToolbar() {
    const toolbar = document.getElementById("toolbar");
    toolbar.innerHTML = "";

    if (currentUser.role === "manufacturing" || currentUser.role === "engineer") {
        toolbar.innerHTML += `<button onclick="openCreateModal()">+ Create Lot</button>`;
    }
    if (currentUser.role === "engineer") {
        toolbar.innerHTML += `<button onclick="openFamilyModal()">+ Add Family</button>`;
        toolbar.innerHTML += `<button onclick="openPartNumberModal()">+ Add Part Number</button>`;
        toolbar.innerHTML += `<button onclick="openApproveModal()">📋 Pending Approvals</button>`;
    }
    if (currentUser.role === "admin") {
        toolbar.innerHTML += `<button onclick="openUserModal()">+ Create User</button>`;
        toolbar.innerHTML += `<button onclick="openManageUsersModal()">👥 Manage Users</button>`;
    }
}

/* ---- Load Lots ---- */
async function loadLots() {
    const response = await fetch("/lots/");
    const lots = await response.json();
    currentLots = lots;

    const activeBody = document.getElementById("active-body");
    const historyBody = document.getElementById("history-body");
    activeBody.innerHTML = "";
    historyBody.innerHTML = "";

    const activeLots = [];
    const historyLots = [];

    const activeStatuses = [
        "ready_for_audit", "in_audit_process",
        "waiting_me_approval", "waiting_qe_approval"
    ];

    for (const lot of lots) {
        if (activeStatuses.includes(lot.status)) {
            activeLots.push(lot);
        } else {
            historyLots.push(lot);
        }
    }

    historyLots.sort((a, b) => {
        const dateA = a.audited_at || "";
        const dateB = b.audited_at || "";
        return dateB.localeCompare(dateA);
    });

    for (const lot of activeLots) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status.replace(/_/g, " ")}</span>`;
        const actions = buildActions(lot);

        activeBody.innerHTML += `
            <tr>
                <td>${lot.lot_id}</td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family || "-"}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
                <td>${actions}</td>
            </tr>
        `;
    }

    const limit = 7;
    const lotsToShow = historyExpanded ? historyLots : historyLots.slice(0, limit);

    for (const lot of lotsToShow) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status.replace(/_/g, " ")}</span>`;

        historyBody.innerHTML += `
            <tr>
                <td>${lot.lot_id}</td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family || "-"}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
                <td>${lot.ncr_number || "-"}</td>
            </tr>
        `;
    }

    const showMoreContainer = document.getElementById("show-more-container");
    if (historyLots.length > limit) {
        const remaining = historyLots.length - limit;
        showMoreContainer.innerHTML = historyExpanded
            ? `<button class="btn-cancel" onclick="toggleHistory()">Show less</button>`
            : `<button class="btn-cancel" onclick="toggleHistory()">+ Show ${remaining} more</button>`;
    } else {
        showMoreContainer.innerHTML = "";
    }
}

function buildActions(lot) {
    const role = currentUser ? currentUser.role : null;
    let actions = "";

    if (lot.status === "ready_for_audit" && role === "auditor") {
        actions += `<button onclick="openAuditModal(${lot.batch_id})">Audit</button>`;
    }
    if (lot.status === "in_audit_process" && role === "auditor") {
        actions += `<button onclick="openDisposition(${lot.batch_id})">Dispose</button>`;
    }
    if (["hold", "waiting_me_approval", "waiting_qe_approval"].includes(lot.status)
        && (role === "engineer" || role === "manufacturing")) {
        let label = "Sign Return";
        if (lot.status === "waiting_me_approval") label = "Sign (ME pending)";
        else if (lot.status === "waiting_qe_approval") label = "Sign (QE pending)";
        actions += `<button class="btn-sign" onclick="openReturnModal(${lot.batch_id})">${label}</button>`;
    }
    return actions;
}

function toggleHistory() {
    historyExpanded = !historyExpanded;
    loadLots();
}

/* ---- Product Family modal ---- */
function openFamilyModal() {
    document.getElementById("family-modal").style.display = "flex";
}

function closeFamilyModal() {
    document.getElementById("family-modal").style.display = "none";
    document.getElementById("family-form").reset();
}

document.getElementById("family-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = { name: document.getElementById("family-name").value };

    const response = await fetch("/product-families/", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data)
    });

    if (response.ok) {
        closeFamilyModal();
        alert(`Family '${data.name}' proposed. Pending QE approval.`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Part Number modal ---- */
async function openPartNumberModal() {
    const response = await fetch("/product-families/active");
    const families = await response.json();

    const select = document.getElementById("pn-family");
    select.innerHTML = `<option value="">-- Select Family --</option>`;
    for (const f of families) {
        select.innerHTML += `<option value="${f.name}">${f.name}</option>`;
    }

    document.getElementById("part-number-modal").style.display = "flex";
}

function closePartNumberModal() {
    document.getElementById("part-number-modal").style.display = "none";
    document.getElementById("part-number-form").reset();
}

document.getElementById("part-number-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = {
        code: document.getElementById("pn-code").value,
        description: document.getElementById("pn-description").value,
        family_name: document.getElementById("pn-family").value
    };

    const response = await fetch("/part-numbers/", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data)
    });

    if (response.ok) {
        closePartNumberModal();
        alert(`Part number '${data.code}' proposed. Pending QE approval.`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Create Lot modal ---- */
async function openCreateModal() {
    const response = await fetch("/part-numbers/active");
    const partNumbers = await response.json();

    const select = document.getElementById("part_number_code");
    select.innerHTML = `<option value="">-- Select Part Number --</option>`;
    for (const pn of partNumbers) {
        select.innerHTML += `<option value="${pn.code}">${pn.code} — ${pn.description}</option>`;
    }

    document.getElementById("create-modal").style.display = "flex";
}

function closeCreateModal() {
    document.getElementById("create-modal").style.display = "none";
    document.getElementById("create-lot-form").reset();
}

document.getElementById("create-lot-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const newLot = {
        lot_id: document.getElementById("lot_id").value,
        part_number_code: document.getElementById("part_number_code").value,
        units: parseInt(document.getElementById("units").value),
        manufacturing_date: document.getElementById("manufacturing_date").value,
        status: "ready_for_audit"
    };

    const response = await fetch("/lots/", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(newLot)
    });

    if (response.ok) {
        const createdLot = await response.json();
        closeCreateModal();
        loadLots();
        alert(`Lot ${createdLot.lot_id} created successfully`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Audit modal ---- */
function openAuditModal(batchId) {
    document.getElementById("audit-lot-form").dataset.batchId = batchId;
    document.getElementById("audit-modal").style.display = "flex";
}

function cancelAudit() {
    document.getElementById("audit-modal").style.display = "none";
    document.getElementById("audit-lot-form").reset();
}

document.getElementById("audit-lot-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const batchId = this.dataset.batchId;
    const body = {
        username: document.getElementById("audit-username").value,
        password: document.getElementById("audit-password").value
    };

    const response = await fetch(`/lots/${batchId}/audit`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (response.ok) {
        cancelAudit();
        loadLots();
        alert("Audit process started successfully");
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Disposition modal ---- */
let dispositionBatchId = null;

function openDisposition(batchId) {
    const lot = currentLots.find(l => l.batch_id === batchId);
    if (!lot) return;

    dispositionBatchId = batchId;

    document.getElementById("disp-lot-id").textContent = lot.lot_id;
    document.getElementById("disp-part-number").textContent = lot.part_number_code;
    document.getElementById("disp-description").textContent = lot.part_number_description || "-";
    document.getElementById("disp-family").textContent = lot.product_family || "-";
    document.getElementById("disp-units").textContent = lot.units;

    if (lot.audited_by) {
        document.getElementById("disp-auditor-name").textContent =
            lot.audited_by.first_name + " " + lot.audited_by.last_name;
        document.getElementById("disp-auditor-user").textContent = lot.audited_by.system_user;
    }
    document.getElementById("disp-audited-at").textContent = lot.audited_at || "-";

    document.getElementById("ncr-section").style.display = "none";
    document.getElementById("confirm-hold-btn").style.display = "none";
    document.getElementById("ncr-number").value = "";

    document.getElementById("disposition-modal").style.display = "flex";
}

function showNcrField() {
    document.getElementById("ncr-section").style.display = "block";
    document.getElementById("confirm-hold-btn").style.display = "inline-block";
}

function closeDisposition() {
    document.getElementById("disposition-modal").style.display = "none";
    dispositionBatchId = null;
}

async function submitDisposition(decision) {
    const body = { decision };

    if (decision === "hold") {
        const ncr = document.getElementById("ncr-number").value.trim();
        if (!ncr) {
            alert("NCR number is required to place a lot on hold");
            return;
        }
        body.ncr_number = ncr;
    }

    const response = await fetch(`/lots/${dispositionBatchId}/disposition`, {
        method: "PATCH",
        headers: authHeaders(),
        body: JSON.stringify(body)
    });

    if (response.ok) {
        closeDisposition();
        loadLots();
        alert(`Lot dispositioned as ${decision}`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
}

/* ---- Return from Hold modal ---- */
let returnBatchId = null;

function openReturnModal(batchId) {
    const lot = currentLots.find(l => l.batch_id === batchId);
    if (!lot) return;

    returnBatchId = batchId;

    document.getElementById("return-lot-info").textContent =
        `Lot ${lot.lot_id} — NCR: ${lot.ncr_number || "-"}`;

    let pending = "";
    if (lot.status === "waiting_me_approval") pending = "Waiting for Manufacturing signature";
    else if (lot.status === "waiting_qe_approval") pending = "Waiting for QE Engineer signature";
    else pending = "Requires both Manufacturing and QE Engineer signatures";

    document.getElementById("return-pending-info").textContent = pending;
    document.getElementById("return-modal").style.display = "flex";
}

function closeReturnModal() {
    document.getElementById("return-modal").style.display = "none";
    document.getElementById("return-form").reset();
    returnBatchId = null;
}

document.getElementById("return-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const body = {
        username: document.getElementById("return-username").value,
        password: document.getElementById("return-password").value
    };

    const response = await fetch(`/lots/${returnBatchId}/return-from-hold`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (response.ok) {
        const result = await response.json();
        closeReturnModal();
        loadLots();
        if (result.status === "ready_for_audit") {
            alert("Both signatures received. Lot returned to Ready for Audit.");
        } else {
            alert("Signature recorded. Waiting for the second signature.");
        }
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Pending Approvals modal ---- */
async function openApproveModal() {
    const [familiesRes, pnRes] = await Promise.all([
        fetch("/product-families/"),
        fetch("/part-numbers/")
    ]);
    const families = await familiesRes.json();
    const partNumbers = await pnRes.json();

    const pendingFamilies = families.filter(f => f.status === "pending_qe_approval");
    const pendingPNs = partNumbers.filter(p => p.status === "pending_qe_approval");

    let html = "";

    if (pendingFamilies.length === 0 && pendingPNs.length === 0) {
        html = "<p>No pending approvals.</p>";
    }

    if (pendingFamilies.length > 0) {
        html += "<h3>Product Families</h3>";
        for (const f of pendingFamilies) {
            html += `
                <div class="approve-item">
                    <span>${f.name} — proposed by ${f.proposed_by}</span>
                    <button onclick="approveFamily('${f.name}')">Approve</button>
                </div>
            `;
        }
    }

    if (pendingPNs.length > 0) {
        html += "<h3>Part Numbers</h3>";
        for (const pn of pendingPNs) {
            html += `
                <div class="approve-item">
                    <span>${pn.code} — ${pn.description} — proposed by ${pn.proposed_by}</span>
                    <button onclick="approvePN('${pn.code}')">Approve</button>
                </div>
            `;
        }
    }

    document.getElementById("approve-list").innerHTML = html;
    document.getElementById("approve-modal").style.display = "flex";
}

function closeApproveModal() {
    document.getElementById("approve-modal").style.display = "none";
}

async function approveFamily(name) {
    const response = await fetch(`/product-families/${name}/approve`, {
        method: "PATCH",
        headers: authHeaders()
    });
    if (response.ok) {
        alert(`Family '${name}' approved`);
        openApproveModal();
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
}

async function approvePN(code) {
    const response = await fetch(`/part-numbers/${code}/approve`, {
        method: "PATCH",
        headers: authHeaders()
    });
    if (response.ok) {
        alert(`Part number '${code}' approved`);
        openApproveModal();
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
}

/* ---- Create User modal ---- */
function openUserModal() {
    document.getElementById("user-modal").style.display = "flex";
}

function closeUserModal() {
    document.getElementById("user-modal").style.display = "none";
    document.getElementById("user-form").reset();
}

document.getElementById("user-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const data = {
        username: document.getElementById("user-username").value,
        password: document.getElementById("user-password").value,
        first_name: document.getElementById("user-firstname").value,
        last_name: document.getElementById("user-lastname").value,
        role: document.getElementById("user-role").value
    };

    const response = await fetch("/users/", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data)
    });

    if (response.ok) {
        closeUserModal();
        alert(`User '${data.username}' created successfully`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Manage Users modal ---- */
async function openManageUsersModal() {
    const response = await fetch("/users/", { headers: authHeaders() });
    const users = await response.json();

    let html = `
        <table class="users-table">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const user of users) {
        const isActive = user.is_active === "true";
        const statusBadge = isActive
            ? `<span class="badge-active">Active</span>`
            : `<span class="badge-inactive">Inactive</span>`;

        const roleOptions = ["admin", "manufacturing", "engineer", "auditor"]
            .map(r => `<option value="${r}" ${r === user.role ? "selected" : ""}>${r}</option>`)
            .join("");

        html += `
            <tr>
                <td>${user.username}</td>
                <td>${user.first_name} ${user.last_name}</td>
                <td>
                    <select id="role-${user.username}" class="role-select">
                        ${roleOptions}
                    </select>
                    <button onclick="changeRole('${user.username}')" style="padding:4px 10px;font-size:0.8rem;margin-left:6px;">Save</button>
                </td>
                <td>${statusBadge}</td>
                <td>
                    <button onclick="toggleUser('${user.username}')" class="${isActive ? 'btn-hold' : 'btn-release'}" style="padding:4px 14px;font-size:0.8rem;">
                        ${isActive ? "Deactivate" : "Activate"}
                    </button>
                </td>
            </tr>
        `;
    }

    html += `</tbody></table>`;
    document.getElementById("manage-users-list").innerHTML = html;
    document.getElementById("manage-users-modal").style.display = "flex";
}

function closeManageUsersModal() {
    document.getElementById("manage-users-modal").style.display = "none";
}

async function toggleUser(username) {
    const response = await fetch(`/users/${username}/toggle-active`, {
        method: "PATCH",
        headers: authHeaders()
    });
    if (response.ok) {
        openManageUsersModal();
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
}

async function changeRole(username) {
    const role = document.getElementById(`role-${username}`).value;
    const response = await fetch(`/users/${username}/role`, {
        method: "PATCH",
        headers: authHeaders(),
        body: JSON.stringify({ role })
    });
    if (response.ok) {
        alert(`Role updated to '${role}'`);
        openManageUsersModal();
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
}