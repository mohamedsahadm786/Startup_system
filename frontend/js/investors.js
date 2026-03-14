let currentInvestorId = null;

async function loadInvestorDashboard() {
    requireAuth();

    document.getElementById("welcomeMsg").textContent =
        "👋 Welcome, " + getUserName();

    await loadMyInvestorProfile();
    await loadAllStartups();
    await loadAllInvestors();
}

async function loadMyInvestorProfile() {
    const token = getToken();
    const userId = parseInt(getUserId());

    try {
        const response = await fetch(`${API_URL}/investors/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const investors = await response.json();
        const myProfile = investors.find(i => i.user_id === userId);

        if (myProfile) {
            currentInvestorId = myProfile.id;
            showInvestorCard(myProfile);
        }

    } catch (error) {
        showError("Could not load investor profile.");
    }
}

function showInvestorCard(profile) {
    document.getElementById("investorForm").style.display = "none";
    document.getElementById("investorCard").style.display = "block";

    document.getElementById("cardFirmName").textContent = profile.firm_name;
    document.getElementById("cardFocusAreas").textContent = profile.focus_areas;
    document.getElementById("cardTicketSize").textContent = profile.ticket_size;
    document.getElementById("cardBio").textContent = profile.bio || "";
}

function editInvestorProfile() {
    document.getElementById("investorForm").style.display = "block";
    document.getElementById("investorCard").style.display = "none";
    document.getElementById("investorFormTitle").textContent =
        "Update Your Investor Profile";

    document.getElementById("firmName").value =
        document.getElementById("cardFirmName").textContent;
    document.getElementById("focusAreas").value =
        document.getElementById("cardFocusAreas").textContent;
    document.getElementById("ticketSize").value =
        document.getElementById("cardTicketSize").textContent;
    document.getElementById("bio").value =
        document.getElementById("cardBio").textContent;
}

async function saveInvestorProfile() {
    const token = getToken();

    const body = {
        firm_name: document.getElementById("firmName").value.trim(),
        focus_areas: document.getElementById("focusAreas").value.trim(),
        ticket_size: document.getElementById("ticketSize").value.trim(),
        bio: document.getElementById("bio").value.trim() || null
    };

    if (!body.firm_name || !body.focus_areas || !body.ticket_size) {
        showError("Please fill in all required fields.");
        return;
    }

    try {
        let response;

        if (currentInvestorId) {
            response = await fetch(`${API_URL}/investors/${currentInvestorId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify(body)
            });
        } else {
            response = await fetch(`${API_URL}/investors/`, {
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
            showError(data.detail || "Could not save profile.");
            return;
        }

        currentInvestorId = data.id;
        showSuccess("Investor profile saved!");
        showInvestorCard(data);

    } catch (error) {
        showError("Could not connect to server.");
    }
}

async function loadAllStartups() {
    const token = getToken();
    const container = document.getElementById("startupsList");

    try {
        const response = await fetch(`${API_URL}/startups/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const startups = await response.json();

        if (!response.ok || startups.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <p>No startups found on the platform yet.</p>
                </div>`;
            return;
        }

        const cards = await Promise.all(startups.map(async (startup) => {

            // ── Fetch AI Evaluation ──
            let scoreHtml = `
                <p style="color:#888; font-size:13px; margin-top:12px;">
                    Not evaluated yet
                </p>`;

            try {
                const evalRes = await fetch(
                    `${API_URL}/startups/${startup.id}/evaluation`,
                    { headers: { "Authorization": "Bearer " + token } }
                );
                if (evalRes.ok) {
                    const evalData = await evalRes.json();
                    scoreHtml = `
                        <div style="margin-top:12px;">
                            <div class="score-badge">${evalData.score} / 100</div>
                            <p style="color:#4ade80; font-size:13px; margin-top:8px;">
                                ✅ ${evalData.strengths}
                            </p>
                            <p style="color:#f87171; font-size:13px; margin-top:4px;">
                                ⚠️ ${evalData.weaknesses}
                            </p>
                            <p style="color:#60a5fa; font-size:13px; margin-top:4px;">
                                💡 ${evalData.suggestions}
                            </p>
                        </div>`;
                }
            } catch (e) {}

            // ── Fetch Pitch Deck Analysis ──
            let pitchHtml = "";

            try {
                const pitchRes = await fetch(
                    `${API_URL}/startups/${startup.id}/pitch-deck`,
                    { headers: { "Authorization": "Bearer " + token } }
                );
                if (pitchRes.ok) {
                    const pitchData = await pitchRes.json();
                    if (pitchData.score) {
                        pitchHtml = `
                            <div style="margin-top:16px; padding-top:16px;
                                border-top:1px solid rgba(255,255,255,0.08);">
                                <p style="color:#a78bfa; font-size:13px;
                                    font-weight:600; margin-bottom:8px;">
                                    📊 Pitch Deck Score: ${pitchData.score} / 100
                                </p>
                                <p style="color:#ccc; font-size:13px; line-height:1.7;">
                                    ${pitchData.analysis || ""}
                                </p>
                            </div>`;
                    }
                }
            } catch (e) {}

            return `
                <div class="card">
                    <h3>${startup.name}</h3>
                    <p>${startup.description}</p>
                    <p style="margin-top:8px; color:#aaa; font-size:13px;">
                        🏭 ${startup.industry} &nbsp;|&nbsp; 📈 ${startup.stage}
                    </p>
                    ${scoreHtml}
                    ${pitchHtml}
                </div>`;
        }));

        container.innerHTML = cards.join("");

    } catch (error) {
        container.innerHTML = `
            <div class="card"><p>Could not load startups.</p></div>`;
    }
}

async function loadAllInvestors() {
    const token = getToken();
    const container = document.getElementById("investorsList");

    try {
        const response = await fetch(`${API_URL}/investors/`, {
            headers: { "Authorization": "Bearer " + token }
        });

        const investors = await response.json();

        if (!response.ok || investors.length === 0) {
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

window.onload = loadInvestorDashboard;