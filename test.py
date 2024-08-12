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