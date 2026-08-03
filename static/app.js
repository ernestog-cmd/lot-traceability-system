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