document.addEventListener("DOMContentLoaded", function() {

    // 🔹 Get references to HTML elements
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultsSection = document.getElementById("resultsSection");
    const fileInput = document.getElementById("resumeFile"); 
    const skillsList = document.getElementById("skillsList");
    const jobRolesList = document.getElementById("jobRolesList");
    const aboutBtn = document.getElementById("aboutBtn");
const modal = document.getElementById("aboutModal");
const closeModal = document.getElementById("closeModal");


    analyzeBtn.addEventListener("click", async (event) => {

        event.preventDefault();

        // 1️⃣ Check if file is selected
        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a resume first!");
            return;
        }

        // 2️⃣ Prepare FormData to send to backend
        const formData = new FormData();
        formData.append("resume", file); 

        try {
            // 3️⃣ Send POST request to Flask backend
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("Server responded with error " + response.status);
            }

            const data = await response.json();
            const overallScore = data.overall_score || 0;


            // 4️⃣ Show results section AFTER successful response
            resultsSection.style.display = "flex";

            

            // 6️⃣ Display skills
            skillsList.innerHTML = ""; 

            const matchedSkills = data.matched_skills || [];

            if (matchedSkills.length === 0) {
                const li = document.createElement("li");
                li.innerText = "No skills matched";
                skillsList.appendChild(li);
            } else {
                matchedSkills.forEach(skill => {
                    const li = document.createElement("li");
                    li.innerText = skill;
                    skillsList.appendChild(li);
                });
            }
            // Display predicted job roles
jobRolesList.innerHTML = "";

const roles = data.predicted_roles || [];

if (roles.length === 0) {
    const li = document.createElement("li");
    li.innerText = "No roles calculated";
    jobRolesList.appendChild(li);
} else {
    roles.forEach(item => {
        const li = document.createElement("li");
        li.innerText = item.role + " — " + item.match + "% eligible";
        jobRolesList.appendChild(li);
    });
}
const scoreFeedback = document.getElementById("scoreFeedback");
scoreFeedback.innerHTML = "";

const message = document.createElement("div");

if (overallScore >= 60) {
    message.innerText = "👍 Strong Resume! Overall Score: " + overallScore + "%";
} else {
    message.innerText = "👎 Needs Improvement! Overall Score: " + overallScore + "%";
}

scoreFeedback.appendChild(message);


        } catch (error) {
            console.error("Error:", error);
            alert("Something went wrong. Check backend terminal.");
        }
    });
        // -------- About Modal Logic --------

    aboutBtn.addEventListener("click", function (e) {
        e.preventDefault();
        modal.style.display = "flex";
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Optional: close when clicking outside modal box
    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

});

