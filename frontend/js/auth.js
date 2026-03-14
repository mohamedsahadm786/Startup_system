// The base URL of your FastAPI backend
const API_URL = "http://127.0.0.1:8000";


// ─────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────

function showError(message) {
    const el = document.getElementById("errorMsg");
    el.textContent = message;
    el.style.display = "block";
    // Hide success if showing
    const success = document.getElementById("successMsg");
    if (success) success.style.display = "none";
}

function showSuccess(message) {
    const el = document.getElementById("successMsg");
    el.textContent = message;
    el.style.display = "block";
    // Hide error if showing
    const error = document.getElementById("errorMsg");
    if (error) error.style.display = "none";
}

function saveUserToStorage(data) {
    // Save JWT token and user info to localStorage
    // This is how the frontend "remembers" who is logged in
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("name", data.name);
}

function getToken() {
    return localStorage.getItem("token");
}

function getRole() {
    return localStorage.getItem("role");
}

function getUserId() {
    return localStorage.getItem("user_id");
}

function getUserName() {
    return localStorage.getItem("name");
}

function logout() {
    // Clear everything from localStorage and go to login page
    localStorage.clear();
    window.location.href = "login.html";
}

// If user is not logged in, redirect to login page
// Call this at the top of every dashboard page
function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = "login.html";
    }
}

// ─────────────────────────────────────────────
// SIGNUP
// ─────────────────────────────────────────────

async function handleSignup() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    // Basic validation
    if (!name || !email || !password) {
        showError("Please fill in all fields");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password, role })
        });

        const data = await response.json();

        if (!response.ok) {
            // Show the error message from the backend
            showError(data.detail || "Signup failed. Please try again.");
            return;
        }

        // Signup successful — redirect to login
        showSuccess("Account created! Redirecting to login...");
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);

    } catch (error) {
        showError("Cannot connect to server. Make sure the backend is running.");
    }
}


// ─────────────────────────────────────────────
// LOGIN
// ─────────────────────────────────────────────

async function handleLogin() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        showError("Please fill in all fields");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Login failed. Check your credentials.");
            return;
        }

        // Save token and user info
        saveUserToStorage(data);

        showSuccess("Login successful! Redirecting...");

        // Redirect based on role
        setTimeout(() => {
            if (data.role === "founder") {
                window.location.href = "founder_dashboard.html";
            } else if (data.role === "investor") {
                window.location.href = "investor_dashboard.html";
            }
        }, 1000);

    } catch (error) {
        showError("Cannot connect to server. Make sure the backend is running.");
    }
}