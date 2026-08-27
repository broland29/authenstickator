/* Scripts for login.html */

async function addPasswordInputListener() {
    const passwordInput = document.getElementById("passwordInput")
    const unlockButton = document.getElementById("unlockButton")
    passwordInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            unlockButton.click()
        }
    })
}

async function unlockHandler() {
    const password = document.getElementById("passwordInput").value;
    const result = await callApi(() =>
        window.pywebview.api.login.verify_password_handler(password))

    if (result.status === RESPONSE.STATUS_SUCCESS) {
        await loadView(result.data);
    }
}
