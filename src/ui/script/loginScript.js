async function initLogin() {
    console.log("View login initialized.")
}

async function unlockHandler() {
    const password = document.getElementById("passwordInput").value;
    const result = await callApi(() => window.pywebview.api.login.verify_password_handler(password))

    if (result.status === CONSTANTS.STATUS_SUCCESS) {
        await loadView(result.data);
    }
}
