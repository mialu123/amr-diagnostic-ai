async function simulate() {

    const resultDiv = document.getElementById("result");

    const policy = document.getElementById("policy").value;

    if (!policy.trim()) {
        alert("Please enter a policy.");
        return;
    }

    resultDiv.innerHTML = `
        <div class="card">
            <h2>⏳ Analyzing Policy Impact...</h2>
            <p>Evaluating impacts across multiple communities.</p>
        </div>
    `;

    try {

        const response = await fetch("/simulate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                policy: policy
            })
        });

        const result = await response.json();

        if (result.error) {
            resultDiv.innerHTML = `
                <div class="card error-card">
                    <h2>❌ Error</h2>
                    <p>${result.error}</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="card">
                <h2>📜 Policy Analysis</h2>
                <p>${policy}</p>
            </div>
        `;

        result.perspectives.forEach(group => {

            let badgeColor = "#6b7280";

            if (group.opinion === "Support") badgeColor = "#22c55e";
            if (group.opinion === "Oppose") badgeColor = "#ef4444";
            if (group.opinion === "Mixed") badgeColor = "#f59e0b";

            html += `
                <div class="card demographic-card">

                    <h2>${group.group}</h2>

                    <div class="opinion-badge"
                         style="background:${badgeColor};">
                        ${group.opinion}
                    </div>

                    <p>
                        <strong>Impact Score:</strong>
                        ${group.impact_score}
                    </p>

                    <p>${group.summary}</p>

                    <h3>✅ Benefits</h3>

                    <ul>
                        ${group.benefits.map(
                            b => `<li>${b}</li>`
                        ).join("")}
                    </ul>

                    <h3>⚠️ Concerns</h3>

                    <ul>
                        ${group.concerns.map(
                            c => `<li>${c}</li>`
                        ).join("")}
                    </ul>

                </div>
            `;
        });

        resultDiv.innerHTML = html;

    } catch (error) {

        resultDiv.innerHTML = `
            <div class="card error-card">
                <h2>❌ Connection Error</h2>
                <p>Could not connect to the FastAPI server.</p>
            </div>
        `;

        console.error(error);
    }
}