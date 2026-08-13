let timerIntervalId = null;

/**
 * To be called when switching to this view.
 */
async function initApp() {  // todo: maybe a nice callback instead of manual call?
    await addAllSecretsHandler();
    startUpdateTimers();
    console.log("View app initialized.")
}

function startUpdateTimers() {
    if (timerIntervalId !== null) {
        return;
    }
    timerIntervalId = setInterval(updateTimers, 1000);
}

function updateTimers() {
    const rowElements = document.querySelectorAll(".rowDiv");
    for (const rowElement of rowElements) {
        const expiresAt = Number(rowElement.dataset.expiresAt);
        const remainingMs = expiresAt - Date.now();

        if (remainingMs <= 0) {
            promoteNextCode(rowElement);
            refreshCodesAndExpirationTimes(rowElement);
            continue;
        }
        // frontend mathematics
        rowElement.querySelector(".remainingTimeAnchor").textContent = Math.ceil(remainingMs / 1000);
    }
}

function promoteNextCode(row) {
    row.dataset.expiresAt = row.dataset.nextExpiresAt;
    row.querySelector(".currentCodeAnchor").textContent = row.dataset.nextCode;
}

async function refreshCodesAndExpirationTimes(rowElement) {
    const name = rowElement.dataset.name;
    const data = await callApi(() => window.pywebview.api.app.get_codes_and_expiration_times(name))
    if (data === null) {
        return;
    }
    rowElement.dataset.currentCode = data.current_code;
    rowElement.dataset.nextCode = data.next_code;
    rowElement.dataset.expiresAt = data.expires_at;
    rowElement.dataset.nextExpiresAt = data.next_expires_at;
}


/**
 * Load all secrets.
 */
async function addAllSecretsHandler() {
    const results = await window.pywebview.api.app.add_all_secrets_handler();
    for (const result of results) {
        await addRow(data.name, data.current_code, data.next_code, data.expires_at);
    }
}

/**
 * Add a secret to the storage, get data, and display it.
 */
async function addSecretHandler() {
    const secretValue = document.getElementById("secretInput").value;
    const nameValue = document.getElementById("nameInput").value;

    const data = await callApi(() => window.pywebview.api.app.add_secret_handler(secretValue, nameValue))
    if (data === null) {
        return;
    }
    await addRow(data.name, data.current_code, data.next_code, data.expires_at, data.next_expires_at);
}

/**
 * Add a rowDiv (containing name, code and time remaining related to a secret) to rowsDiv.
 */
async function addRow(name, currentCode, nextCode, expiresAt, nextExpiresAt) {
    const rowsElement = document.getElementById("rowsDiv");

    const rowElement = document.createElement("div");
    rowElement.className = "rowDiv";
    rowElement.id = name + "RowDiv";

    // needed for removal
    rowElement.dataset.name = name;

    // needed for instant next code retrieval
    rowElement.dataset.currentCode = currentCode;
    rowElement.dataset.nextCode = nextCode;
    rowElement.dataset.expiresAt = expiresAt;
    rowElement.dataset.nextExpiresAt = nextExpiresAt;

    const remainingMs = expiresAt - Date.now();
    const remainingS = Math.ceil(remainingMs / 1000);

    const buttonId = name + "RemoveSecretButton";
    rowElement.innerHTML = `
            <hr>
            <p><a>Name: </a> <a>${name}</a></p>
            <p><a>Code: </a> <a class = "currentCodeAnchor">${currentCode}</a></p>
            <p><a>Remaining time: </a> <a class = "remainingTimeAnchor">${remainingS}</a></p>
            <button id = "${buttonId}" onclick="removeSecretHandler(this)">Remove</button>
            <hr>
        `
    rowsElement.appendChild(rowElement);
}


/**
 * Remove the rowDiv containing buttonElement.
 */
async function removeSecretHandler(buttonElement) {
    const rowElement = buttonElement.closest(".rowDiv");
    const name = rowElement.dataset.name;

    await window.pywebview.api.app.remove_secret_handler(name);

    rowElement.remove();
}
