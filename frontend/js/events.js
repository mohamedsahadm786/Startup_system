// ─────────────────────────────────────────────
// Load page
// ─────────────────────────────────────────────

async function loadEventsPage() {
    requireAuth();

    document.getElementById("welcomeMsg").textContent =
        "👋 Welcome, " + getUserName();

    // Show networking section only for founders
    if (getRole() === "founder") {
        document.getElementById("networkingSection").style.display = "block";
    }

    await loadAllEvents();
}


// ─────────────────────────────────────────────
// Go back to correct dashboard based on role
// ─────────────────────────────────────────────

function goToDashboard() {
    if (getRole() === "founder") {
        window.location.href = "founder_dashboard.html";
    } else {
        window.location.href = "investor_dashboard.html";
    }
}


// ─────────────────────────────────────────────
// Create a new event
// ─────────────────────────────────────────────

async function createEvent() {
    const token = getToken();

    const body = {
        title: document.getElementById("eventTitle").value.trim(),
        event_date: document.getElementById("eventDate").value.trim(),
        location: document.getElementById("eventLocation").value.trim(),
        description: document.getElementById("eventDescription").value.trim()
    };

    if (!body.title || !body.event_date || !body.location || !body.description) {
        showError("Please fill in all fields.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/events/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Could not create event.");
            return;
        }

        showSuccess("Event created successfully!");

        // Clear form
        document.getElementById("eventTitle").value = "";
        document.getElementById("eventDate").value = "";
        document.getElementById("eventLocation").value = "";
        document.getElementById("eventDescription").value = "";

        // Reload events list
        await loadAllEvents();

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// ─────────────────────────────────────────────
// Load all events
// ─────────────────────────────────────────────

async function loadAllEvents() {
    const token = getToken();
    const container = document.getElementById("eventsList");

    try {
        const response = await fetch(`${API_URL}/events/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const events = await response.json();

        if (!response.ok || events.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <p>No events yet. Be the first to create one!</p>
                </div>`;
            return;
        }

        const userId = parseInt(getUserId());

        container.innerHTML = events.map(event => `
            <div class="card">
                <h3>${event.title}</h3>
                <p>${event.description}</p>
                <p style="color:#aaa; font-size:13px; margin-top:10px;">
                    📅 ${event.event_date} &nbsp;|&nbsp;
                    📍 ${event.location}
                </p>
                ${event.created_by === userId ? `
                    <div style="margin-top:14px; display:flex; gap:10px;">
                        <button class="btn-secondary"
                            onclick="deleteEvent(${event.id})"
                            style="font-size:13px; padding:8px 16px;">
                            🗑️ Delete
                        </button>
                    </div>` : ""}
            </div>
        `).join("");

    } catch (error) {
        container.innerHTML = `
            <div class="card"><p>Could not load events.</p></div>`;
    }
}


// ─────────────────────────────────────────────
// Delete an event
// ─────────────────────────────────────────────

async function deleteEvent(eventId) {
    const token = getToken();

    try {
        const response = await fetch(`${API_URL}/events/${eventId}`, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });

        if (!response.ok) {
            const data = await response.json();
            showError(data.detail || "Could not delete event.");
            return;
        }

        showSuccess("Event deleted.");
        await loadAllEvents();

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// Load page on open
window.onload = loadEventsPage;