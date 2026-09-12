let currentLots = [];
let historyExpanded = false;

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

    for (const lot of lots) {
        if (lot.status === "ready_for_audit" || lot.status === "in_audit_process") {
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
        const statusCell = `<span class="status status-${lot.status}">${lot.status}</span>`;

        let actions = "";
        if (lot.status === "ready_for_audit") {
            actions = `<button onclick="openAuditModal(${lot.batch_id})">Audit</button>`;
        } else if (lot.status === "in_audit_process") {
            actions = `<button onclick="openDisposition(${lot.batch_id})">Dispose</button>`;
        }

        activeBody.innerHTML += `
            <tr>
                <td>${lot.lot_id}</td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family}</td>
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
        const statusCell = `<span class="status status-${lot.status}">${lot.status}</span>`;

        historyBody.innerHTML += `
            <tr>
                <td>${lot.lot_id}</td>
                <td>${lot.part_number_code}</td>
                <td>${lot.part_number_description || "-"}</td>
                <td>${lot.product_family}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
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

function toggleHistory() {
    historyExpanded = !historyExpanded;
    loadLots();
}

/* ---- Part Number modal ---- */
function openPartNumberModal() {
    document.getElementById("part-number-modal").style.display = "block";
}

function closePartNumberModal() {
    document.getElementById("part-number-modal").style.display = "none";
    document.getElementById("part-number-form").reset();
}

const partNumberForm = document.getElementById("part-number-form");
partNumberForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = {
        code: document.getElementById("pn-code").value,
        description: document.getElementById("pn-description").value
    };

    const response = await fetch("/part-numbers/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        closePartNumberModal();
        alert(`Part number ${data.code} added successfully`);
    } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
    }
});

/* ---- Create Lot modal ---- */
async function openCreateModal() {
    const response = await fetch("/part-numbers/");
    const partNumbers = await response.json();

    const select = document.getElementById("part_number_code");
    select.innerHTML = `<option value="">-- Select Part Number --</option>`;
    for (const pn of partNumbers) {
        select.innerHTML += `<option value="${pn.code}">${pn.code} — ${pn.description}</option>`;
    }

    document.getElementById("create-modal").style.display = "block";
}

function closeCreateModal() {
    document.getElementById("create-modal").style.display = "none";
    document.getElementById("create-lot-form").reset();
}

const form = document.getElementById("create-lot-form");
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const newLot = {
        lot_id: document.getElementById("lot_id").value,
        part_number_code: document.getElementById("part_number_code").value,
        product_family: document.getElementById("product_family").value,
        units: parseInt(document.getElementById("units").value),
        manufacturing_date: document.getElementById("manufacturing_date").value,
        status: "ready_for_audit"
    };

    const response = await fetch("/lots/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
    document.getElementById("audit-lot-id").textContent = batchId;
    document.getElementById("audit-lot-form").dataset.batchId = batchId;
    document.getElementById("audit-modal").style.display = "block";
}

function cancelAudit() {
    document.getElementById("audit-modal").style.display = "none";
    document.getElementById("audit-lot-form").reset();
}

const auditForm = document.getElementById("audit-lot-form");
auditForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const batchId = auditForm.dataset.batchId;

    const auditor = {
        first_name: document.getElementById("auditor_first_name").value,
        last_name: document.getElementById("auditor_last_name").value,
        system_user: document.getElementById("auditor_system_user").value
    };

    const response = await fetch(`/lots/${batchId}/audit`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(auditor)
    });

    if (response.ok) {
        cancelAudit();
        loadLots();
        alert(`Lot assigned correctly. Audit process has started`);
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
    document.getElementById("disp-family").textContent = lot.product_family;
    document.getElementById("disp-units").textContent = lot.units;

    if (lot.audited_by) {
        document.getElementById("disp-auditor-name").textContent =
            lot.audited_by.first_name + " " + lot.audited_by.last_name;
        document.getElementById("disp-auditor-user").textContent = lot.audited_by.system_user;
    }
    document.getElementById("disp-audited-at").textContent = lot.audited_at || "-";

    document.getElementById("disposition-modal").style.display = "block";
}

function closeDisposition() {
    document.getElementById("disposition-modal").style.display = "none";
    dispositionBatchId = null;
}

async function submitDisposition(decision) {
    const response = await fetch(`/lots/${dispositionBatchId}/disposition?decision=${decision}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" }
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

loadLots();