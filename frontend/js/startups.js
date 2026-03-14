let currentStartupId = null;

async function loadMyStartup() {
    requireAuth();

    document.getElementById("welcomeMsg").textContent =
        "👋 Welcome, " + getUserName();

    const token = getToken();
    const userId = parseInt(getUserId());

    try {
        const response = await fetch(`${API_URL}/startups/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const startups = await response.json();
        const myStartup = startups.find(s => s.founder_id === userId);

        if (myStartup) {
            currentStartupId = myStartup.id;
            showStartupCard(myStartup);
            loadEvaluation();
            loadPitchDeck();
        }

    } catch (error) {
        showError("Could not load startup data.");
    }
}

function showStartupCard(startup) {
    document.querySelector(".dashboard-form").style.display = "none";
    document.getElementById("startupCard").style.display = "block";

    document.getElementById("cardName").textContent = startup.name;
    document.getElementById("cardDescription").textContent = startup.description;
    document.getElementById("cardIndustry").textContent = startup.industry;
    document.getElementById("cardStage").textContent = startup.stage;
    document.getElementById("cardWebsite").textContent = startup.website || "N/A";
}

function editStartup() {
    document.querySelector(".dashboard-form").style.display = "block";
    document.getElementById("startupCard").style.display = "none";
    document.getElementById("formTitle").textContent = "Update Your Startup";

    document.getElementById("startupName").value =
        document.getElementById("cardName").textContent;
    document.getElementById("startupDescription").value =
        document.getElementById("cardDescription").textContent;
    document.getElementById("startupIndustry").value =
        document.getElementById("cardIndustry").textContent;
    document.getElementById("startupStage").value =
        document.getElementById("cardStage").textContent;
}

async function saveStartup() {
    const token = getToken();

    const body = {
        name: document.getElementById("startupName").value.trim(),
        description: document.getElementById("startupDescription").value.trim(),
        industry: document.getElementById("startupIndustry").value.trim(),
        stage: document.getElementById("startupStage").value.trim(),
        website: document.getElementById("startupWebsite").value.trim() || null
    };

    if (!body.name || !body.description || !body.industry || !body.stage) {
        showError("Please fill in all required fields.");
        return;
    }

    try {
        let response;

        if (currentStartupId) {
            response = await fetch(`${API_URL}/startups/${currentStartupId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify(body)
            });
        } else {
            response = await fetch(`${API_URL}/startups/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify(body)
            });
        }

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Could not save startup.");
            return;
        }

        currentStartupId = data.id;
        showSuccess("Startup saved successfully!");
        showStartupCard(data);

    } catch (error) {
        showError("Could not connect to server.");
    }
}

// ─────────────────────────────────────────────
// Load all investors for founder to see
// ─────────────────────────────────────────────

async function loadAllInvestorsForFounder() {
    const token = getToken();
    const container = document.getElementById("founderInvestorsList");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/investors/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const investors = await response.json();

        if (!Array.isArray(investors) || investors.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <p>No investor profiles found yet.</p>
                </div>`;
            return;
        }

        container.innerHTML = investors.map(inv => `
            <div class="card">
                <h3>${inv.firm_name}</h3>
                <p style="color:#aaa; font-size:13px; margin-top:6px;">
                    🎯 ${inv.focus_areas}
                </p>
                <p style="color:#aaa; font-size:13px; margin-top:4px;">
                    💰 ${inv.ticket_size}
                </p>
                <p style="color:#ccc; font-size:14px; margin-top:10px;">
                    ${inv.bio || ""}
                </p>
            </div>
        `).join("");

    } catch (error) {
        container.innerHTML = `
            <div class="card"><p>Could not load investors.</p></div>`;
    }
}

// ─────────────────────────────────────────────
// Init — runs both loaders on page open
// ─────────────────────────────────────────────

async function initFounderDashboard() {
    await loadMyStartup();
    await loadAllInvestorsForFounder();
}

window.onload = initFounderDashboard;