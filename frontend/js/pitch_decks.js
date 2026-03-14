// ─────────────────────────────────────────────
// Load existing pitch deck analysis
// ─────────────────────────────────────────────

async function loadPitchDeck() {
    if (!currentStartupId) return;

    const token = getToken();

    try {
        const response = await fetch(
            `${API_URL}/startups/${currentStartupId}/pitch-deck`,
            { headers: { "Authorization": "Bearer " + token } }
        );

        if (response.ok) {
            const data = await response.json();
            if (data.score) {
                showPitchCard(data);
            } else {
                document.getElementById("noPitchMsg").style.display = "block";
                document.getElementById("pitchCard").style.display = "none";
            }
        } else {
            document.getElementById("noPitchMsg").style.display = "block";
            document.getElementById("pitchCard").style.display = "none";
        }

    } catch (error) {
        document.getElementById("noPitchMsg").style.display = "block";
    }
}


// ─────────────────────────────────────────────
// Show pitch deck result card
// ─────────────────────────────────────────────

function showPitchCard(data) {
    document.getElementById("pitchCard").style.display = "block";
    document.getElementById("noPitchMsg").style.display = "none";

    document.getElementById("pitchScore").textContent =
        data.score ? data.score + " / 100" : "N/A";
    document.getElementById("pitchAnalysis").textContent =
        data.analysis || "Analysis not available yet.";
}


// ─────────────────────────────────────────────
// Upload pitch deck PDF
// ─────────────────────────────────────────────

async function uploadPitchDeck() {
    if (!currentStartupId) {
        showError("Please save your startup first.");
        return;
    }

    const fileInput = document.getElementById("pitchFile");
    if (!fileInput.files.length) {
        showError("Please select a PDF file first.");
        return;
    }

    const token = getToken();
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    showSuccess("Uploading PDF...");

    try {
        const response = await fetch(
            `${API_URL}/startups/${currentStartupId}/upload-pitch-deck`,
            {
                method: "POST",
                headers: { "Authorization": "Bearer " + token },
                body: formData
                // Note: do NOT set Content-Type here
                // The browser sets it automatically for FormData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Upload failed.");
            return;
        }

        showSuccess("PDF uploaded successfully! Now click Analyze with AI.");

    } catch (error) {
        showError("Could not connect to server.");
    }
}


// ─────────────────────────────────────────────
// Analyze pitch deck with AI
// ─────────────────────────────────────────────

async function analyzePitchDeck() {
    if (!currentStartupId) {
        showError("Please save your startup first.");
        return;
    }

    const token = getToken();
    showSuccess("Analyzing pitch deck with AI... please wait.");

    try {
        const response = await fetch(
            `${API_URL}/startups/${currentStartupId}/analyze-pitch-deck`,
            {
                method: "POST",
                headers: { "Authorization": "Bearer " + token }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Analysis failed.");
            return;
        }

        showSuccess("Pitch deck analysis complete!");
        showPitchCard(data);

    } catch (error) {
        showError("Could not connect to server.");
    }
}