const API_BASE_URL = "http://localhost:8000";
let websocket;

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
      const response = await fetch(`${API_BASE_URL}/interview/${applicantId}`, {
        method: "POST",
      });
      const data = await response.json();

      document.getElementById("interviewSection").style.display = "block";
      document.getElementById(
        "messages"
      ).innerHTML = `<div class="message ai">${data.text}</div>`;
      document.getElementById("audioPlayer").src = data.audio_url;

      // Initialize WebSocket
      websocket = new WebSocket(
        `ws://localhost:8000/ws?applicant_id=${applicantId}`
      );

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        document.getElementById(
          "messages"
        ).innerHTML += `<div class="message ai">${data.text}</div>`;
        document.getElementById("audioPlayer").src = data.audio_url;
      };

      websocket.onclose = () => {
        console.log("WebSocket closed");
      };

      websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Error starting interview:", error);
    }
  });

document
  .getElementById("startRecording")
  .addEventListener("click", async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Media devices not supported.");
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);

    const audioChunks = [];
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      sendAudio(audioBlob);
    };

    mediaRecorder.start();
    document.getElementById("startRecording").textContent = "Recording...";
    setTimeout(() => {
      mediaRecorder.stop();
      document.getElementById("startRecording").textContent = "Start Recording";
    }, 5000); // Record for 5 seconds
  });

const sendAudio = (audioBlob) => {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(audioBlob);
  }
};
