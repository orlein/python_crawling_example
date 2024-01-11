async function loadJSON(filename) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.overrideMimeType("application/json");
    xhr.open("GET", filename, true); // Replace 'appDataServices' with the path to your file
    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4 && xhr.status == "200") {
        // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode

        resolve(JSON.parse(xhr.responseText));
      }
    };
    xhr.send(null);
  });
}

function populateTableHeader(tableId, headerKeys) {
  const table = document.getElementById(tableId);
  const tableHeader = table.querySelector("thead");
  const firstRow = tableHeader.querySelector("tr");
  firstRow.innerHTML = "";
  headerKeys.forEach((key) => {
    const th = document.createElement("th");
    th.textContent = key;
    firstRow.appendChild(th);
  });
}

function populateTableBody(tableId, data) {
  const table = document.getElementById(tableId);
  const tableBody = table.querySelector("tbody");
  tableBody.innerHTML = "";
  data.forEach((row) => {
    const tr = document.createElement("tr");
    Object.keys(row).forEach((key) => {
      const td = document.createElement("td");
      td.textContent = row[key];
      tr.appendChild(td);
    });
    tableBody.appendChild(tr);
  });
}

function parseDataHeader(data) {
  const header = data[0];
  const headerKeys = Object.keys(header);
  return headerKeys;
}

function onClickButton() {
  loadJSON("./kream_data.json").then((data) => {
    const headerKeys = parseDataHeader(data);
    populateTableHeader("data-table", headerKeys);
    populateTableBody("data-table", data);
  });
}
