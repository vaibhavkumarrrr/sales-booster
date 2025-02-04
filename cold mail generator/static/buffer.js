function processJob() {
    const jobUrl = document.getElementById("job-url").value;
    if (!jobUrl) {
        alert("Please enter a job URL.");
        return;
    }

    // Show loader and clear output
    document.getElementById("loader").style.display = "block";
    document.getElementById("output").innerHTML = "";

    fetch("/process-job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_url: jobUrl }),
    })
    .then(response => response.json())
    .then(data => {
        // Hide loader
        document.getElementById("loader").style.display = "none";

        if (data.error) {
            document.getElementById("output").innerHTML = "Error: " + data.error;
        } else {
            document.getElementById("output").innerHTML = `
                <h3>Generated Email:</h3>
                <p>${data.email}</p>
                <h3>Portfolio Links:</h3>
                <p>${data.portfolio_links}</p>
                
            `;
        }
    })
    .catch(error => {
        // Hide loader and show error
        document.getElementById("loader").style.display = "none";
        document.getElementById("output").innerHTML = "Error: " + error.message;
    });
}