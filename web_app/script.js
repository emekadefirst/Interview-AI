const API_BASE_URL = "http://localhost:8000";

document
  .getElementById("startInterview")
  .addEventListener("click", async () => {
    const applicantId = document.getElementById("applicantId").value;
    if (!applicantId) {
      alert("Please enter an applicant ID.");
      return;
    }

    // Start the interview
    try {
      const response = await fetch(`${API_BASE_URL}/apiinterview/${applicantId}`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      document.getElementById("interviewSection").style.display = "block";
      document.getElementById("responseText").textContent = data.text;
      document.getElementById("audioPlayer").src = data.audio_url;
    } catch (error) {
      console.error("Error fetching interview data:", error);
      alert("Failed to start interview. Please check the console for details.");
    }
  });
