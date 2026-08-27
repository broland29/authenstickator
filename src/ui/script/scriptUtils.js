/* Scripts and constants shared between the other script files. */

const FETCH_ERROR = (path) => `Fetching from path ${path} failed`;

/**
 * Convenience wrapper for calling an API function: handles showing error/success messages, returns
 * the whole result for possible further processing.
 */
async function callApi(apiFunction, silent = false) {
    const result = await apiFunction();

    if (!silent) {
        clearMessage();
        if (result.status === RESPONSE.STATUS_ERROR) {
            showError(result.error_message);
        } else if (result.status === RESPONSE.STATUS_SUCCESS && result.success_message !== null) {
            showSuccess(result.success_message);
        }
    }

    return result;
}

/**
 * Shows a scary error message to the user.
 */
function showError(errorMessage) {
    const messageParagraph = document.getElementById("messageParagraph");
    if (!messageParagraph) {
        console.error("Cannot log error message since messageParagraph was not found.")
        return;
    }
    messageParagraph.classList.remove("success-message")  // does not fail if not in class list
    messageParagraph.classList.add("error-message")
    messageParagraph.textContent = errorMessage;
}

/**
 * Shows a friendly success message to the user.
 */
function showSuccess(successMessage) {
    const messageParagraph = document.getElementById("messageParagraph");
    if (!messageParagraph) {
        console.error("Cannot log success message since messageParagraph was not found.")
        return;
    }
    messageParagraph.classList.remove("error-message")  // does not fail if not in class list
    messageParagraph.classList.add("success-message")
    messageParagraph.textContent = successMessage;
}

function clearMessage() {
    document.getElementById("messageParagraph").textContent = "";
}

/**
 * Changes the view (inside index.html) to the view at path viewPath.
 */
async function loadView(viewPath) {
    // If fetch succeeds, response.ok is still false, The response is not a regular HTTP response.
    // Success is signaled by status 0.
    const response = await fetch(viewPath);
    if (response.status !== 0) {
        throw new Error(FETCH_ERROR(viewPath));
    }
    document.getElementById("viewDiv").innerHTML = await response.text();

    // If registering, now the register elements are ready, event listeners can be added.
    if (viewPath.endsWith("register.html")) {
        await addNewPasswordInputListener();
    }
    // If logging in, now login elements are ready, event listeners can be added,
    if (viewPath.endsWith("login.html")) {
        await addPasswordInputListener();
    }
    // The TOTP view requires extra initialization after it is loaded.
    if (viewPath.endsWith("totp.html")) {
        await initTOTP();
    }
}
