# <!DOCTYPE html>
# <html lang="en">

# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>AI Interview</title>
#     <style>
#         /* Basic styles for layout */
#         body {
#             font-family: Arial, sans-serif;
#             margin: 0;
#             padding: 0;
#         }

#         #video-container {
#             display: flex;
#             justify-content: center;
#             margin: 20px;
#         }

#         video {
#             border: 1px solid #ccc;
#             width: 40%;
#             border-radius: 10px;
#         }

#         #messages {
#             margin: 20px;
#         }

#         .message {
#             margin: 10px 0;
#         }

#         .message .text {
#             font-weight: bold;
#         }

#         #record-controls {
#             display: flex;
#             justify-content: center;
#             margin: 20px;
#         }

#         button {
#             margin: 0 10px;
#         }
#     </style>
# </head>

# <body>
#     <h1>Interview Room</h1>
#     <div id="video-container">
#         <video id="webcam" autoplay></video>
#     </div>
#     <div id="record-controls">
#         <button id="start-recording">Start Recording</button>
#         <button id="stop-recording" disabled>Stop Recording</button>
#     </div>
#     <div id="messages"></div>
#     <script>
#         const video = document.getElementById('webcam');
#         const startRecordingBtn = document.getElementById('start-recording');
#         const stopRecordingBtn = document.getElementById('stop-recording');
#         let mediaRecorder;
#         let audioChunks = [];

#         navigator.mediaDevices.getUserMedia({ video: true, audio: true })
#             .then(stream => {
#                 video.srcObject = stream;

#                 mediaRecorder = new MediaRecorder(stream);
#                 mediaRecorder.ondataavailable = event => {
#                     audioChunks.push(event.data);
#                 };

#                 mediaRecorder.onstop = () => {
#                     const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
#                     const audioUrl = URL.createObjectURL(audioBlob);
#                     audioChunks = [];
#                     addMessage('You', audioUrl);
#                 };

#                 startRecordingBtn.addEventListener('click', () => {
#                     mediaRecorder.start();
#                     startRecordingBtn.disabled = true;
#                     stopRecordingBtn.disabled = false;
#                 });

#                 stopRecordingBtn.addEventListener('click', () => {
#                     mediaRecorder.stop();
#                     startRecordingBtn.disabled = false;
#                     stopRecordingBtn.disabled = true;
#                 });
#             })
#             .catch(error => {
#                 console.error('Error accessing webcam: ', error);
#             });

#         function addMessage(text, audioUrl) {
#             const messageDiv = document.createElement('div');
#             messageDiv.className = 'message';

#             const textDiv = document.createElement('div');
#             textDiv.className = 'text';
#             textDiv.textContent = text;

#             const audio = document.createElement('audio');
#             audio.controls = true;
#             audio.src = audioUrl;

#             messageDiv.appendChild(textDiv);
#             messageDiv.appendChild(audio);

#             document.getElementById('messages').appendChild(messageDiv);
#         }

#         // Fetch initial messages
#         fetch('http://127.0.0.1:8000/apiinterview/4', {
#             method: 'POST',
#             headers: {
#                 'Content-Type': 'application/json'
#             },
#             body: JSON.stringify({})
#         })
#             .then(response => response.json())
#             .then(data => {
#                 data.messages.forEach(msg => {
#                     addMessage(msg.text, msg.audio_url);
#                 });
#             })
#             .catch(error => {
#                 console.error('Error fetching messages: ', error);
#             });
#     </script>
# </body>

# </html>

    # <!-- <script>

    #     let mediaRecorder;

    #     let audioChunks = [];

    #     document.addEventListener('DOMContentLoaded', () => {

    #         const meetingCode = localStorage.getItem('meetingCode');

    #         if (!meetingCode) {

    #             alert('No meeting code found. Please enter a meeting code first.');

    #             window.location.href = 'door.html';

    #         }

    #     });

    #     function startRecording() {

    #         navigator.mediaDevices.getUserMedia({ audio: true })

    #             .then(stream => {

    #                 mediaRecorder = new MediaRecorder(stream);

    #                 mediaRecorder.start();

    #                 mediaRecorder.addEventListener("dataavailable", event => {

    #                     audioChunks.push(event.data);

    #                 });

    #                 document.querySelector('button[onclick="startRecording()"]').style.display = 'none';

    #                 document.querySelector('button[onclick="stopRecording()"]').style.display = 'inline-block';

    #             });

    #     }

    #     function stopRecording() {

    #         mediaRecorder.stop();

    #         mediaRecorder.addEventListener("stop", () => {

    #             const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

    #             sendAudioToServer(audioBlob);

    #         });

    #         document.querySelector('button[onclick="startRecording()"]').style.display = 'inline-block';

    #         document.querySelector('button[onclick="stopRecording()"]').style.display = 'none';

    #     }

    #     function sendAudioToServer(audioBlob) {

    #         const meetingCode = localStorage.getItem('meetingCode');

    #         const formData = new FormData();

    #         formData.append('audio', audioBlob);

    #         fetch(`http://127.0.0.1:8000/api/interview/${meetingCode}`, {

    #             method: 'POST',

    #             body: formData

    #         })

    #             .then(response => response.json())

    #             .then(data => {

    #                 document.getElementById('responseArea').innerText = data.text;

    #                 const audioPlayer = document.getElementById('audioPlayer');

    #                 audioPlayer.src = data.audio_url;

    #                 audioPlayer.style.display = 'block';

    #             })

    #             .catch(error => {

    #                 console.error('Error:', error);

    #                 document.getElementById('responseArea').innerText = 'Error occurred while processing the request.';

    #             });

    #     }

    # </script> -->
    # <script>
    #     let applicantId = null;
    #     let mediaRecorder;
    #     let audioChunks = [];

    #     document.addEventListener('DOMContentLoaded', function () {
    #         const meetingCode = sessionStorage.getItem('meetingCode');

    #         if (!meetingCode) {
    #             alert('No meeting code found.');
    #             return;
    #         }

    #         startInterview(meetingCode);
    #     });

    #     async function startInterview(meetingCode) {
    #         try {
    #             const formData = new FormData();
    #             formData.append('number', meetingCode);

    #             const response = await fetch(`http://127.0.0.1:8000/apiinterview/${meetingCode}`, {
    #                 method: 'POST',
    #                 body: formData
    #             });

    #             if (!response.ok) {
    #                 throw new Error('Network response was not ok');
    #             }

    #             const data = await response.json();
    #             applicantId = data.id;
    #             document.getElementById('startBtn').disabled = true;
    #             document.getElementById('recordBtn').disabled = false;
    #             addMessage(data.text, 'ai');
    #             playAudio(data.audio_url);
    #         } catch (error) {
    #             console.error('Error starting interview:', error);
    #             addMessage("Error: Unable to start the interview. Please try again.", 'ai');
    #             document.getElementById('startBtn').disabled = false;
    #         }
    #     }

    #     async function sendAudioToServer() {
    #         const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    #         const formData = new FormData();
    #         formData.append('audio_response', audioBlob, 'response.wav');

    #         try {
    #             const response = await fetch(`http://127.0.0.1:8000/apply/interview/${applicantId}`, {
    #                 method: 'POST',
    #                 body: formData
    #             });

    #             if (!response.ok) {
    #                 throw new Error('Network response was not ok');
    #             }

    #             const data = await response.json();

    #             addMessage(`You: ${data.applicant_text}`, 'applicant');
    #             addMessage(data.text, 'ai');
    #             playAudio(data.audio_url);
    #         } catch (error) {
    #             console.error('Error sending audio to server:', error);
    #             addMessage("Error: Unable to process your response. Please try again.", 'ai');
    #         }
    #     }

    #     function addMessage(message, sender) {
    #         const messageElement = document.createElement('div');
    #         messageElement.classList.add('message', sender);
    #         messageElement.textContent = message.replace('## InAS: ', '').trim();
    #         document.getElementById('chatArea').appendChild(messageElement);
    #         document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;

    #         // Also display AI response in the response area
    #         if (sender === 'ai') {
    #             document.getElementById('responseArea').textContent = messageElement.textContent;
    #         }
    #     }

    #     function playAudio(audioUrl) {
    #         const audio = new Audio(audioUrl);
    #         audio.onerror = () => {
    #             console.error('Error playing audio.');
    #             addMessage("Error: Unable to play the audio. Please try again later.", 'ai');
    #         };
    #         audio.play().catch(error => {
    #             console.error('Error playing audio:', error);
    #         });
    #     }
    # </script> -->

        
