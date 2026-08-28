/* Scripts for changepassword.html */

async function addChangePasswordInputListener() {
    const changePasswordOldInput = document.getElementById("changePasswordOldInput")
    const changePasswordNewInput = document.getElementById("changePasswordNewInput")
    const changePasswordApplyButton = document.getElementById("changePasswordApplyButton")
    await clickButtonIfEnter(changePasswordOldInput, changePasswordApplyButton);
    await clickButtonIfEnter(changePasswordNewInput, changePasswordApplyButton);
}

async function changePasswordApplyHandler() {
    const oldPassword = document.getElementById("changePasswordOldInput").value;
    const newPassword = document.getElementById("changePasswordNewInput").value;
    const result = await callApi(() =>
        window.pywebview.api.change_password.change_password_handler(oldPassword, newPassword))

    if (result.status === RESPONSE.STATUS_SUCCESS) {
        const changePasswordButton = document.getElementById("changePasswordButton");
        const changePasswordDiv = document.getElementById("changePasswordDiv");
        changePasswordDiv.innerHTML = "";
        changePasswordButton.innerText = "Change password"
    }
}
