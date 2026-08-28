/* Scripts for totp.html */

let totpIntervalID = null;

/**
 * To be called when switching to this html, after TOTPController is fully initialized.
 */
async function initTOTP() {
    await addSecretInputListener();
    await getAllInfo();
    await startTOTPTimer();
}

async function addSecretInputListener() {
    const nameInput = document.getElementById("nameInput")
    const secretInput = document.getElementById("secretInput")
    const addSecretButton = document.getElementById("addSecretButton")
    await clickButtonIfEnter(nameInput, addSecretButton);
    await clickButtonIfEnter(secretInput, addSecretButton);
}

/**
 * Asks for all the information.
 */
async function getAllInfo() {
    const result = await window.pywebview.api.totp.get_all_info_handler();
    if (result.status !== RESPONSE.STATUS_SUCCESS) {
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
    if (totpIntervalID !== null) {
        return;
    }
    totpIntervalID = setInterval(updateTimers, 1000);  // Call each second.
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
        rowElement.querySelector(".remainingTimeAnchor").textContent =
            Math.ceil(remainingMs / 1000);
    }
}

/**
 * Takes the "cached" next code and expiration time and uses them as current.
 */
function promoteNextCode(rowElement) {
    rowElement.dataset.expiresAt = rowElement.dataset.nextExpiresAt;
    rowElement.querySelector(".currentCodeAnchor").textContent = rowElement.dataset.nextCode;
    rowElement.querySelector(".remainingTimeAnchor").textContent = rowElement.dataset.interval;
}

/**
 * Gets info for secret associated with the name inside rowElement, stores result in dataset.
 */
async function getInfoHandler(rowElement) {
    const name = rowElement.dataset.name;
    const result = await callApi(() =>
        window.pywebview.api.totp.get_info_handler(name), true)
    if (result.status !== RESPONSE.STATUS_SUCCESS) {
        return;
    }
    rowElement.dataset.currentCode = result.data.current_code;
    rowElement.dataset.nextCode = result.data.next_code;
    rowElement.dataset.expiresAt = result.data.expires_at;
    rowElement.dataset.nextExpiresAt = result.data.next_expires_at;
    rowElement.dataset.interval = result.data.interval;
}

/**
 * Adds a secret to the storage based on user input, and displays info.
 */
async function addSecretHandler() {
    const secretInput = document.getElementById("secretInput")
    const nameInput = document.getElementById("nameInput")
    const secret = secretInput.value;
    const name = nameInput.value;

    const result = await callApi(() =>
        window.pywebview.api.totp.add_secret_handler(secret, name))
    if (result.status !== RESPONSE.STATUS_SUCCESS) {
        return;
    }

    // Name is re-sent from the backend - not optimal, but happens just at adding. Worth the
    // compromise for simplicity.
    await addRow(result.data);

    // Wipe inputs.
    secretInput.value = "";
    nameInput.value = "";
}

/**
 * Delegates initiation of image dialog for the QR code, and displays info.
 */
async function addSecretQRHandler() {
    const result = await callApi(() => window.pywebview.api.totp.add_secret_qr_handler())
    if (result.status !== RESPONSE.STATUS_SUCCESS) {
        return;
    }

    await addRow(result.data)
}

/**
 * Remove a secret and the associated rowDiv.
 */
async function removeSecretHandler(buttonElement) {
    const rowElement = buttonElement.closest(".rowDiv");
    const name = rowElement.dataset.name;

    const result = await callApi(() => window.pywebview.api.totp.remove_secret_handler(name));
    if (result.status !== RESPONSE.STATUS_SUCCESS) {
        return;
    }

    rowElement.remove();
}

/**
 * The changePasswordButton is a toggle. If the button's text is "Cancel", switches it to
 * "Change password" and hides the change password html. Otherwise, switches text to "Cancel" and
 * shows the change password html.
 */
async function changePasswordHandler() {
    const changePasswordButton = document.getElementById("changePasswordButton");
    const changePasswordDiv = document.getElementById("changePasswordDiv");
    if (changePasswordButton.innerText === "Cancel") {
        changePasswordDiv.innerHTML = "";
        changePasswordButton.innerText = "Change password"
        return;
    }
    // On Linux, file:// protocol, succeeds is response.ok=false, response.status=0.
    // On Windows, HTTP protocol, success is response.ok=true, response.status=200.
    // So for both cases, failure can be expressed as response.ok=false, response.status !==0
    const response = await fetch(VIEW_PATH.CHANGE_PASSWORD)
    if (!response.ok && response.status !== 0) {
        throw new Error(FETCH_ERROR(VIEW_PATH.CHANGE_PASSWORD));
    }
    changePasswordDiv.innerHTML = await response.text();
    changePasswordButton.innerText = "Cancel";

    // Add listeners here, since elements newly added.
    await addChangePasswordInputListener();
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
    const interval = info.interval;

    const rowsElement = document.getElementById("rowsDiv");

    const rowElement = document.createElement("div");
    rowElement.className = "rowDiv";
    rowElement.id = name + "RowDiv";

    // Name needed for removal.
    rowElement.dataset.name = name;

    // Data needed for promotion of the next code.
    rowElement.dataset.currentCode = currentCode;
    rowElement.dataset.nextCode = nextCode;
    rowElement.dataset.expiresAt = expiresAt;
    rowElement.dataset.nextExpiresAt = nextExpiresAt;
    rowElement.dataset.interval = interval;

    const remainingMs = expiresAt - Date.now();
    const remainingS = Math.ceil(remainingMs / 1000);

    const buttonId = name + "RemoveSecretButton";
    rowElement.innerHTML = `
            <p><a>Name: </a> <a>${name}</a></p>
            <p><a>Code: </a> <a class = "currentCodeAnchor">${currentCode}</a></p>
            <p><a>Remaining time: </a> <a class = "remainingTimeAnchor">${remainingS}</a></p>
            <button id = "${buttonId}" onclick="removeSecretHandler(this)">Remove</button>
            <hr>
        `
    rowsElement.appendChild(rowElement);
}
