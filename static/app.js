async function loadLots() {
    const response = await fetch("/lots");
    const lots = await response.json();

    const tableBody = document.getElementById("lots-body");
    tableBody.innerHTML = "";

    for (const lot of lots) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";

        let actions = "";
        if (lot.status === "ready_for_audit") {
            actions = `<button onclick="auditLot('${lot.id}')">Audit</button>`;
        }

        const row = `
            <tr>
                <td>${lot.id}</td>
                <td>${lot.part_number}</td>
                <td>${lot.description}</td>
                <td>${lot.product_family}</td>
                <td>${lot.units}</td>
                <td>${lot.status}</td>
                <td>${auditor}</td>
                <td>${actions}</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    }
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
        form.reset();
        loadLots();
        alert(`Lot ${createdLot.id} created successfully`);
    } else {
        alert("Error creating lot");
    }
});

function auditLot(lotId) {
    document.getElementById("audit-lot-id").textContent = lotId;
    document.getElementById("audit-lot-form").style.display = "block";
    document.getElementById("audit-lot-form").dataset.lotId = lotId;
}

function cancelAudit() {
    document.getElementById("audit-lot-form").style.display = "none";
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
        auditForm.style.display = "none";
        auditForm.reset();
        loadLots();
        alert(`Lot ${lotId} audited successfully`);
    } else {
        alert("Error auditing lot");
    }
});

loadLots();