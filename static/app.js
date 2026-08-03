async function loadLots() {
    const response = await fetch("/lots");
    const lots = await response.json();
    console.log(lots);

    const tableBody = document.getElementById("lots-body");
    tableBody.innerHTML= "";

    for (const lot of lots) {
        const auditor = lot.audited_by ? lot.audited_by.system_user : "-";
        const row = `
            <tr>
                <td>${lot.id}</td>
                <td>${lot.part_number}</td>
                <td>${lot.description}</td>
                <td>${lot.product_family}</td>
                <td>${lot.units}</td>
                <td>${lot.status}</td>
                <td>${auditor}</td>
            </tr>
        `; 
        tableBody.innerHTML += row;
    }
}
loadLots();

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
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify(newLot)
    });

    if (response.ok) {
        const createdLot = await response.json();
        form.reset();
        loadLots();
        alert(`Lot ${createdLot.id} created successfully`);
    } else {
        alert("Error creating lot")
    }
});