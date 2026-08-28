/* Scripts for register.html */

async function addNewPasswordInputListener() {
    const newPasswordInput = document.getElementById("newPasswordInput")
    const newPasswordButton = document.getElementById("newPasswordButton")
    await clickButtonIfEnter(newPasswordInput, newPasswordButton);
}

async function newPasswordHandler() {
    const password = document.getElementById("newPasswordInput").value;
    const result = await callApi(() =>
        window.pywebview.api.register.new_password_handler(password))

    if (result.status === RESPONSE.STATUS_SUCCESS) {
        await loadView(result.data);
    }
}
