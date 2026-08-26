async function addNewPasswordInputListener() {
    const newPasswordInput = document.getElementById("newPasswordInput")
    const newPasswordButton = document.getElementById("newPasswordButton")
    newPasswordInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            newPasswordButton.click()
        }
    })
}

async function newPasswordHandler() {
    const password = document.getElementById("newPasswordInput").value;
    const result = await callApi(() => window.pywebview.api.register.new_password_handler(password))

    if (result.status === CONSTANTS.STATUS_SUCCESS) {
        await loadView(result.data);
    }
}
