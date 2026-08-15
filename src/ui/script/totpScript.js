let totpTimer = null;

/**
 * To be called when switching to this view, after TOTPController is fully initialized.
 */
async function initTOTP() {
    await getAllInfo();
    await startTOTPTimer();
    console.debug("View initialized.")
}

/**
 * Asks for all the info in the storage.
 */
async function getAllInfo() {
    const result = await window.pywebview.api.totp.get_all_info_handler();
    if (result.status !== CONSTANTS.STATUS_SUCCESS) {
        return;
    }
    for (const info of result.data) {
        await addRow(info);
    }
}

/**
 * Starts a repeated call to updateTimers.
 */
async function startTOTPTimer() {
    if (totpTimer !== null) {
        return;
    }
    totpTimer = setInterval(updateTimers, 1000);
}

/**
 * Updates the remaining time and current code for each row. Called repeatedly.
 */
function updateTimers() {
    const rowElements = document.querySelectorAll(".rowDiv");
    for (const rowElement of rowElements) {
        const expiresAt = Number(rowElement.dataset.expiresAt);
        const remainingMs = expiresAt - Date.now();

        // For each expired code, promote the next code and get new info.
        if (remainingMs <= 0) {
            promoteNextCode(rowElement);
            getInfoHandler(rowElement);
            continue;
        }

        // Update the remaining time shown.
        rowElement.querySelector(".remainingTimeAnchor").textContent = Math.ceil(remainingMs / 1000);
    }
}

/**
 * Takes the "cached" next code and expiration time and uses them as current.
 */
function promoteNextCode(rowElement) {
    rowElement.dataset.expiresAt = rowElement.dataset.nextExpiresAt;
    rowElement.querySelector(".currentCodeAnchor").textContent = rowElement.dataset.nextCode;
}

/**
 * Gets info for secret associated with the name inside rowElement.
 */
async function getInfoHandler(rowElement) {
    const name = rowElement.dataset.name;
    const result = await callApi(() => window.pywebview.api.totp.get_info_handler(name), true)
    if (result.status !== CONSTANTS.STATUS_SUCCESS) {
        return;
    }
    rowElement.dataset.currentCode = result.data.current_code;
    rowElement.dataset.nextCode = result.data.next_code;
    rowElement.dataset.expiresAt = result.data.expires_at;
    rowElement.dataset.nextExpiresAt = result.data.next_expires_at;
}

/**
 * Add a secret to the storage, get data, and display it.
 */
async function addSecretHandler() {
    const secret = document.getElementById("secretInput").value;
    const name = document.getElementById("nameInput").value;

    const result = await callApi(() => window.pywebview.api.totp.add_secret_handler(secret, name))
    if (result.status !== CONSTANTS.STATUS_SUCCESS) {
        return;
    }

    // Name is re-sent from the backend - not optimal, but happens just at adding. Worth the
    // compromise for simplicity.
    await addRow(result.data);
}

/**
 * Remove a secret and the associated rowDiv.
 */
async function removeSecretHandler(buttonElement) {
    const rowElement = buttonElement.closest(".rowDiv");
    const name = rowElement.dataset.name;

    const result = await callApi(() => window.pywebview.api.totp.remove_secret_handler(name));
    if (result.status !== CONSTANTS.STATUS_SUCCESS) {
        return;
    }

    rowElement.remove();
}

/**
 * Add a rowDiv (containing name, code and time remaining related to a secret) to rowsDiv.
 */
async function addRow(info) {
    // parse the response from Python
    const name = info.name;
    const currentCode = info.current_code;
    const nextCode = info.next_code;
    const expiresAt = info.expires_at;
    const nextExpiresAt = info.next_expires_at;

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
