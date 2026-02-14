document.addEventListener("DOMContentLoaded", function () {

    // ── Element refs ──
    const analyzeBtn     = document.getElementById("analyzeBtn");
    const btnLoader      = document.getElementById("btnLoader");
    const resultsSection = document.getElementById("resultsSection");
    const fileInput      = document.getElementById("resumeFile");
    const roleSelect     = document.getElementById("roleSelect");
    const skillsList     = document.getElementById("skillsList");
    const jobRolesList   = document.getElementById("jobRolesList");
    const aboutBtn       = document.getElementById("aboutBtn");
    const modal          = document.getElementById("aboutModal");
    const closeModal     = document.getElementById("closeModal");

    let chartInst = null;

    // ── ANALYZE BUTTON ──
    analyzeBtn.addEventListener("click", async () => {

        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a resume first!");
            return;
        }

        // Loading state
        analyzeBtn.disabled = true;
        btnLoader.classList.remove("hidden");

        const formData = new FormData();
        formData.append("resume", file);
        formData.append("role", roleSelect.value);   // send selected role to backend

        try {
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("Server error " + response.status);
            }

            const data = await response.json();

            // Show results section
            resultsSection.style.display = "flex";

            // Render everything
            renderBreakdown(data.score_breakdown);
            renderSkills(data.matched_skills);
            renderJobRoles(data.predicted_roles, data.overall_score);
            renderChart(data.predicted_roles);
            renderSuggestions(data.suggestions);

            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 80);

        } catch (error) {
            console.error("Error:", error);
            alert("Something went wrong. Make sure your Flask backend is running on port 5000.");
        } finally {
            analyzeBtn.disabled = false;
            btnLoader.classList.add("hidden");
        }
    });


    // ── RENDER: SCORE BREAKDOWN ──
    function renderBreakdown(bd) {
        if (!bd) return;

        document.getElementById("techNum").textContent = bd.technical.score;
        document.getElementById("expNum").textContent  = bd.experience.score;
        document.getElementById("eduNum").textContent  = bd.education.score;

        // Animate bars after tiny delay so CSS transition fires
        setTimeout(() => {
            document.getElementById("techBar").style.width = (bd.technical.score / 50 * 100) + "%";
            document.getElementById("expBar").style.width  = (bd.experience.score / 30 * 100) + "%";
            document.getElementById("eduBar").style.width  = (bd.education.score  / 20 * 100) + "%";
        }, 60);

        document.getElementById("techKw").textContent = bd.technical.keywords_found + " keywords found";
        document.getElementById("expKw").textContent  = bd.experience.keywords_found + " keywords found";
        document.getElementById("eduKw").textContent  = bd.education.keywords_found  + " keywords found";

        // Total count-up animation
        countUp("totalNum", bd.total, 1000);

        document.getElementById("totalMsg").textContent =
            bd.total >= 70 ? "🏆 Excellent!" :
            bd.total >= 50 ? "👍 Good"        :
                             "🔧 Needs Work";
    }


    // ── RENDER: MATCHED SKILLS (as tags) ──
    function renderSkills(matched) {
        skillsList.innerHTML = "";

        if (!matched || matched.length === 0) {
            skillsList.innerHTML = '<span style="color:#888">No skills matched</span>';
            return;
        }

        matched.forEach((skill, i) => {
            const tag = document.createElement("span");
            tag.className = "skill-tag";
            tag.textContent = skill;
            tag.style.animationDelay = (i * 0.04) + "s";
            skillsList.appendChild(tag);
        });
    }


    // ── RENDER: JOB ROLES LIST + OVERALL FEEDBACK ──
    function renderJobRoles(roles, overallScore) {
        jobRolesList.innerHTML = "";

        if (!roles || roles.length === 0) {
            const li = document.createElement("li");
            li.textContent = "No roles calculated";
            jobRolesList.appendChild(li);
        } else {
            roles.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item.role + " — " + item.match + "% eligible";
                jobRolesList.appendChild(li);
            });
        }

        // Overall feedback (your original style)
        const feedback = document.getElementById("scoreFeedback");
        feedback.innerHTML = "";
        const msg = document.createElement("div");
        msg.textContent = overallScore >= 60
            ? "👍 Strong Resume! Overall Score: " + overallScore + "%"
            : "👎 Needs Improvement! Overall Score: " + overallScore + "%";
        feedback.appendChild(msg);
    }


    // ── RENDER: CHART ──
    function renderChart(roles) {
        if (!roles || roles.length === 0) return;

        const sorted = [...roles].sort((a, b) => b.match - a.match);
        const labels = sorted.map(r => r.role);
        const vals   = sorted.map(r => r.match);

        const colors = vals.map(v =>
            v >= 60 ? "rgba(128,0,128,0.85)" :
            v >= 30 ? "rgba(151,7,71,0.55)"  :
                      "rgba(200,180,200,0.5)"
        );

        if (chartInst) chartInst.destroy();

        chartInst = new Chart(
            document.getElementById("rolesChart").getContext("2d"),
            {
                type: "bar",
                data: {
                    labels,
                    datasets: [{
                        label: "Match %",
                        data: vals,
                        backgroundColor: colors,
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "#800080",
                            titleColor: "white",
                            bodyColor: "white",
                            padding: 10,
                            callbacks: {
                                label: ctx => " " + ctx.parsed.x + "% match"
                            }
                        }
                    },
                    scales: {
                        x: {
                            min: 0, max: 100,
                            ticks: {
                                color: "#555",
                                font: { family: "Arial" },
                                callback: v => v + "%"
                            },
                            grid: { color: "rgba(128,0,128,0.06)" }
                        },
                        y: {
                            ticks: {
                                color: "#333",
                                font: { family: "Arial", size: 13 }
                            },
                            grid: { display: false }
                        }
                    },
                    animation: { duration: 900, easing: "easeOutQuart" }
                }
            }
        );
    }


    // ── RENDER: SUGGESTIONS ──
    function renderSuggestions(suggestions) {
        const sugList = document.getElementById("sugList");
        sugList.innerHTML = "";

        if (!suggestions || suggestions.length === 0) {
            sugList.innerHTML = '<div style="color:#555;font-size:14px">🎉 Great resume! Consider adding certifications to boost further.</div>';
            return;
        }

        suggestions.forEach((s, i) => {
            const card = document.createElement("div");
            card.className = "sug-item";
            card.style.animationDelay = (i * 0.07) + "s";
            card.innerHTML = `
                <div class="sug-ico">${s.icon}</div>
                <div>
                    <div class="sug-t">${s.title}</div>
                    <div class="sug-d">${s.detail}</div>
                </div>
            `;
            sugList.appendChild(card);
        });
    }


    // ── HELPER: count-up animation ──
    function countUp(id, target, duration) {
        const el   = document.getElementById(id);
        const step = target / (duration / 16);
        let cur    = 0;
        const timer = setInterval(() => {
            cur = Math.min(cur + step, target);
            el.textContent = Math.round(cur);
            if (cur >= target) clearInterval(timer);
        }, 16);
    }


    // ── MODAL ──
    aboutBtn.addEventListener("click", function (e) {
        e.preventDefault();
        modal.style.display = "flex";
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

});