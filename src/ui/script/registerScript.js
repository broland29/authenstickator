async function newPasswordHandler() {
    const password = document.getElementById("newPasswordInput").value;
    const result = await callApi(() => window.pywebview.api.register.new_password_handler(password))

    if (result.status === CONSTANTS.STATUS_SUCCESS) {
        await loadView(result.data);
    }
}
