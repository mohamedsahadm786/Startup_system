// ─────────────────────────────────────────────
// Load latest evaluation for current startup
// ─────────────────────────────────────────────

async function loadEvaluation() {
    if (!currentStartupId) return;

    const token = getToken();

    try {
        const response = await fetch(
            `${API_URL}/startups/${currentStartupId}/evaluation`,
            { headers: { "Authorization": "Bearer " + token } }
        );

        if (response.ok) {
            const data = await response.json();
            showEvaluationCard(data);
        } else {
            // No evaluation yet
            document.getElementById("noEvalMsg").style.display = "block";
            document.getElementById("evaluationCard").style.display = "none";
        }

    } catch (error) {
        document.getElementById("noEvalMsg").style.display = "block";
    }
}


// ─────────────────────────────────────────────
// Show evaluation result card
// ─────────────────────────────────────────────

function showEvaluationCard(data) {
    document.getElementById("evaluationCard").style.display = "block";
    document.getElementById("noEvalMsg").style.display = "none";

    document.getElementById("evalScore").textContent = data.score + " / 100";
    document.getElementById("evalStrengths").textContent = data.strengths;
    document.getElementById("evalWeaknesses").textContent = data.weaknesses;
    document.getElementById("evalSuggestions").textContent = data.suggestions;
}


// ─────────────────────────────────────────────
// Trigger AI evaluation
// ─────────────────────────────────────────────

async function triggerEvaluation() {
    if (!currentStartupId) {
        showError("Please save your startup first.");
        return;
    }

    const token = getToken();
    showSuccess("Running AI evaluation... please wait 5 seconds.");

    try {
        const response = await fetch(
            `${API_URL}/startups/${currentStartupId}/evaluate`,
            {
                method: "POST",
                headers: { "Authorization": "Bearer " + token }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Evaluation failed.");
            return;
        }

        showSuccess("AI Evaluation complete!");
        showEvaluationCard(data);

    } catch (error) {
        showError("Could not connect to server.");
    }
}