let mediaRecorder;
let audioChunks = [];

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.addEventListener("dataavailable", (event) => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      document.getElementById(
        "user-messages"
      ).innerHTML += `<p>You:</p><audio controls src="${audioUrl}"></audio>`;
      document.getElementById("send-btn").disabled = false;
    });

    setTimeout(() => {
      mediaRecorder.stop();
    }, 3000); // Record for 3 seconds
  });
}

function sendAudio() {
  // Simulate sending the user's audio and receiving the AI's response
  document.getElementById("send-btn").disabled = true;

  // Simulate AI response after processing the user's audio
  setTimeout(() => {
    // Example AI response data
    const aiResponse = {
      text: "## InAS: \n\nWelcome, Victor, it's a pleasure to meet you. My name is InAS, and I'll be conducting your interview for the Python Developer position today. We'll be discussing your experience, skills, and some technical aspects of the role.  Please feel free to ask any questions you might have along the way.\n\nTo start, your resume highlights a variety of projects, including your 'Store API' utilizing Django, Django REST framework, and SQLite3. Can you elaborate on the design choices you made, particularly why you opted for SQLite3 for this e-commerce application?",
      audio_url:
        "http://127.0.0.1:8000/apply/audio/Victor_Chibuogwu_Chukwuemeka_interview.mp3",
    };

    // Display AI text response
    const aiMessageBox = document.getElementById("ai-messages");
    aiMessageBox.innerHTML += `<p>${aiResponse.text.replace(
      "## InAS:",
      "AI:"
    )}</p>`;

    // Display AI audio response
    aiMessageBox.innerHTML += `<audio controls src="${aiResponse.audio_url}"></audio>`;
  }, 2000);
}

// Start the conversation with an AI message
window.onload = function () {
  const aiInitialResponse = {
    text: "## InAS: \n\nHello! Let's start our conversation.",
    audio_url: "http://127.0.0.1:8000/apply/audio/initial_greeting.mp3",
  };

  const aiMessageBox = document.getElementById("ai-messages");
  aiMessageBox.innerHTML = `<p>${aiInitialResponse.text.replace(
    "## InAS:",
    "AI:"
  )}</p>`;
  aiMessageBox.innerHTML += `<audio controls src="${aiInitialResponse.audio_url}"></audio>`;
};
