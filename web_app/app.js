document
  .getElementById("applicationForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const responseContainer = document.getElementById("responseContainer");

    try {
      const response = await fetch("/apply", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to apply.");
      }

      const data = await response.json();

      if (data.error) {
        responseContainer.innerHTML = `<p>Error: ${data.error}</p>`;
      } else {
        responseContainer.innerHTML = `
                <p><strong>AI's response:</strong> ${data.ai_response.text}</p>
                <audio controls>
                    <source src="data:audio/mp3;base64,${data.ai_response.audio}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            `;
      }
    } catch (error) {
      responseContainer.innerHTML = `<p>Error: ${error.message}</p>`;
    }
  });
