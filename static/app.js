let currentLots = [];
let historyExpanded = false;

async function loadLots() {
    const response = await fetch("/lots");
    const lots = await response.json();
    currentLots = lots;

    const activeBody = document.getElementById("active-body");
    const historyBody = document.getElementById("history-body");
    activeBody.innerHTML = "";
    historyBody.innerHTML = "";

    // Separar lotes activos e históricos
    const activeLots = [];
    const historyLots = [];

    for (const lot of lots) {
        if (lot.status === "ready_for_audit" || lot.status === "in_audit_process") {
            activeLots.push(lot);
        } else {
            historyLots.push(lot);
        }
    }

    // Ordenar historial: más recientes primero (por fecha de auditoría)
    historyLots.sort((a, b) => {
        const dateA = a.audited_at || "";
        const dateB = b.audited_at || "";
        return dateB.localeCompare(dateA);
    });

    // Render activos
    for (const lot of activeLots) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status}</span>`;

        let actions = "";
        if (lot.status === "ready_for_audit") {
            actions = `<button onclick="auditLot('${lot.id}')">Audit</button>`;
        } else if (lot.status === "in_audit_process") {
            actions = `<button onclick="openDisposition('${lot.id}')">Dispose</button>`;
        }

        activeBody.innerHTML += `
            <tr>
                <td>${lot.id}</td>
                <td>${lot.part_number}</td>
                <td>${lot.description}</td>
                <td>${lot.product_family}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
                <td>${actions}</td>
            </tr>
        `;
    }

    // Render historial (con límite de 7 si no está expandido)
    const limit = 7;
    const lotsToShow = historyExpanded ? historyLots : historyLots.slice(0, limit);

    for (const lot of lotsToShow) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const statusCell = `<span class="status status-${lot.status}">${lot.status}</span>`;

        historyBody.innerHTML += `
            <tr>
                <td>${lot.id}</td>
                <td>${lot.part_number}</td>
                <td>${lot.description}</td>
                <td>${lot.product_family}</td>
                <td>${lot.units}</td>
                <td>${statusCell}</td>
                <td>${auditor}</td>
            </tr>
        `;
    }

    // Botón "show more" si hay más de 7
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

/* ---- Create Lot modal ---- */
function openCreateModal() {
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
        id: document.getElementById("id").value,
        part_number: document.getElementById("part_number").value,
        description: document.getElementById("description").value,
        product_family: document.getElementById("product_family").value,
        units: parseInt(document.getElementById("units").value),
        manufacturing_date: document.getElementById("manufacturing_date").value,
        status: "ready_for_audit"
    };

    const response = await fetch("/lots", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newLot)
    });

    if (response.ok) {
        const createdLot = await response.json();
        closeCreateModal();
        loadLots();
        alert(`Lot ${createdLot.id} created successfully`);
    } else {
        alert("Error creating lot");
    }
});

/* ---- Audit modal ---- */
function auditLot(lotId) {
    document.getElementById("audit-lot-id").textContent = lotId;
    document.getElementById("audit-lot-form").dataset.lotId = lotId;
    document.getElementById("audit-modal").style.display = "block";
}

function cancelAudit() {
    document.getElementById("audit-modal").style.display = "none";
    document.getElementById("audit-lot-form").reset();
}

const auditForm = document.getElementById("audit-lot-form");
auditForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const lotId = auditForm.dataset.lotId;

    const auditor = {
        first_name: document.getElementById("auditor_first_name").value,
        last_name: document.getElementById("auditor_last_name").value,
        system_user: document.getElementById("auditor_system_user").value
    };

    const response = await fetch(`/lots/${lotId}/audit`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(auditor)
    });

    if (response.ok) {
        cancelAudit();
        loadLots();
        alert(`Lot ${lotId} assigned correctly. Audit process has started`);
    } else {
        alert("Error auditing lot");
    }
});

/* ---- Disposition modal ---- */
let dispositionLotId = null;

function openDisposition(lotId) {
    const lot = currentLots.find(l => l.id === lotId);
    if (!lot) return;

    dispositionLotId = lotId;

    document.getElementById("disp-lot-id").textContent = lot.id;
    document.getElementById("disp-part-number").textContent = lot.part_number;
    document.getElementById("disp-description").textContent = lot.description;
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
    dispositionLotId = null;
}

async function submitDisposition(decision) {
    const lotId = dispositionLotId;

    const response = await fetch(`/lots/${lotId}/disposition?decision=${decision}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" }
    });

    if (response.ok) {
        closeDisposition();
        loadLots();
        alert(`Lot ${lotId} dispositioned as ${decision}`);
    } else {
        alert("Error dispositioning lot");
    }
}

loadLots();