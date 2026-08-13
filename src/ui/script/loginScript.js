async function initLogin() {
    console.log("View login initialized.")
}

async function unlockHandler() {
    const password = document.getElementById("passwordInput").value;
    await callApi(() => window.pywebview.api.login.verify_password_handler(password))
}
