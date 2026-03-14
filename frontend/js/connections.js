// ─────────────────────────────────────────────
// Send a connection request
// ─────────────────────────────────────────────

async function sendConnection() {
    const token = getToken();
    const receiverId = parseInt(
        document.getElementById("receiverId").value
    );

    if (!receiverId) {
        showError("Please enter a valid User ID.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/connections/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ receiver_id: receiverId })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Could not send request.");
            return;
        }

        showSuccess("Connection request sent!");
        document.getElementById("receiverId").value = "";
        await loadPendingRequests();
        await loadMyConnections();

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// ─────────────────────────────────────────────
// Load pending connection requests (received)
// ─────────────────────────────────────────────

async function loadPendingRequests() {
    const token = getToken();
    const container = document.getElementById("pendingList");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/connections/pending`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await response.json();

        if (!response.ok || data.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <p>No pending requests.</p>
                </div>`;
            return;
        }

        container.innerHTML = data.map(conn => `
            <div class="card">
                <h3>Request from User ID: ${conn.requester_id}</h3>
                <span class="badge">${conn.status}</span>
                <div style="margin-top:14px; display:flex; gap:10px;">
                    <button class="btn-primary"
                        onclick="respondToConnection(${conn.id}, 'accepted')"
                        style="font-size:13px; padding:8px 16px;">
                        ✅ Accept
                    </button>
                    <button class="btn-secondary"
                        onclick="respondToConnection(${conn.id}, 'rejected')"
                        style="font-size:13px; padding:8px 16px;">
                        ❌ Reject
                    </button>
                </div>
            </div>
        `).join("");

    } catch (error) {
        if (container) {
            container.innerHTML = `
                <div class="card"><p>Could not load requests.</p></div>`;
        }
    }
}


// ─────────────────────────────────────────────
// Accept or reject a connection request
// ─────────────────────────────────────────────

async function respondToConnection(connectionId, status) {
    const token = getToken();

    try {
        const response = await fetch(
            `${API_URL}/connections/${connectionId}/respond`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ status })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Could not respond to request.");
            return;
        }

        showSuccess(`Connection ${status}!`);
        await loadPendingRequests();
        await loadMyConnections();

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// ─────────────────────────────────────────────
// Load my connections
// ─────────────────────────────────────────────

async function loadMyConnections() {
    const token = getToken();

    // This works on both events page and founder dashboard
    const container = document.getElementById("myConnectionsList")
        || document.getElementById("connectionsList");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/connections/me`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await response.json();

        if (!response.ok || data.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <p>No connections yet. Send a request to connect!</p>
                </div>`;
            return;
        }

        const userId = parseInt(getUserId());

        container.innerHTML = data.map(conn => {
            const otherUserId = conn.requester_id === userId
                ? conn.receiver_id
                : conn.requester_id;

            return `
                <div class="card">
                    <h3>👤 User ID: ${otherUserId}</h3>
                    <span class="badge">${conn.status}</span>
                    ${conn.status === "pending" && conn.requester_id === userId ? `
                        <div style="margin-top:12px;">
                            <button class="btn-secondary"
                                onclick="cancelConnection(${conn.id})"
                                style="font-size:13px; padding:8px 16px;">
                                ❌ Cancel Request
                            </button>
                        </div>` : ""}
                </div>`;
        }).join("");

    } catch (error) {
        if (container) {
            container.innerHTML = `
                <div class="card"><p>Could not load connections.</p></div>`;
        }
    }
}


// ─────────────────────────────────────────────
// Cancel a connection request
// ─────────────────────────────────────────────

async function cancelConnection(connectionId) {
    const token = getToken();

    try {
        const response = await fetch(
            `${API_URL}/connections/${connectionId}`,
            {
                method: "DELETE",
                headers: { "Authorization": "Bearer " + token }
            }
        );

        if (!response.ok) {
            const data = await response.json();
            showError(data.detail || "Could not cancel request.");
            return;
        }

        showSuccess("Connection request cancelled.");
        await loadMyConnections();

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// Load connections on page open
// Small delay to make sure currentStartupId is set first
setTimeout(() => {
    loadPendingRequests();
    loadMyConnections();
}, 600);
