import os
import base64
from pydantic import BaseModel
from fastapi import APIRouter, File, WebSocket, WebSocketDisconnect, UploadFile
from dotenv import load_dotenv
import speech_recognition as sr  # Importing SpeechRecognition library
from gtts import gTTS
from sessions import applicant_by_id, applicant_chat  # Replace with your session management logic

service = APIRouter()

load_dotenv()

try:
    import google.generativeai as genai
    import pdfplumber
    print("Successfully imported required libraries")
    genai.configure(api_key=os.environ.get('gemini_api'))
    model = genai.GenerativeModel('gemini-1.5-pro')
except ImportError as e:
    print(f"Failed to import libraries: {e}")

class ApplicantInfo(BaseModel):
    fullname: str
    about: str
    role: str

def extract_resume_text(resume_file: UploadFile) -> str:
    with pdfplumber.open(resume_file.file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def generate_interview_prompt(applicant: ApplicantInfo, resume_content: str) -> str:
    return f"""
    You are an experienced AI interviewer for TechCorp. Your task is to conduct a professional and thorough interview with {applicant.fullname} for the position of {applicant.role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:

    Applicant Information:
    - Name: {applicant.fullname}
    - Role applying for: {applicant.role}
    - About: {applicant.about}

    Resume Summary:
    {resume_content}

    Interview Guidelines:
    1. Start with a brief introduction and welcome the candidate.
    2. Ask 5-7 relevant questions based on the role and the applicant's background.
       - Include a mix of:
         - Role-specific technical questions
         - Behavioral questions
         - Situational questions
         - Questions about their experience and skills mentioned in the resume
    3. Allow the candidate to ask 1-2 questions about the role or company.
    4. Conclude the interview professionally.

    Evaluation Criteria:
    - Relevant skills and experience for the {applicant.role} position
    - Problem-solving abilities
    - Communication skills
    - Cultural fit with TechCorp
    - Motivation and enthusiasm for the role

    After the interview, provide a brief summary of the candidate's strengths,
    areas for improvement, and overall suitability for the role.

    Begin the interview now.
    """

def process_applicant(applicant: ApplicantInfo, resume_file: UploadFile):
    try:
        resume_content = extract_resume_text(resume_file)
        prompt = generate_interview_prompt(applicant, resume_content)

        response = model.generate_content(prompt)
        interview_text = response.text if response.text else None

        if interview_text:
            tts = gTTS(text=interview_text, lang='en')
            audio_bytes = tts.get_audio_bytes()
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            return base64_audio
        else:
            return {"error": "Failed to generate interview text"}
    except Exception as e:
        return {"error": f"Internal server error: {e}"}

def process_user_input(audio_data):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_data) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        return f"Error processing audio: {e}"

@service.websocket("/ws/interview/{applicant_id}")
async def interview_websocket(websocket: WebSocket, applicant_id: int):
    await websocket.accept()
    try:
        applicant = applicant_by_id(applicant_id)
        if not applicant:
            await websocket.send_text("Applicant not found")
            await websocket.close()
            return

        ai_message = await process_applicant(applicant, applicant.resume)
        await websocket.send_text(ai_message)
        applicant_chat(applicant_id, f"AI: {ai_message}")

        while True:
            user_audio_data = await websocket.receive_bytes()

            # Save received audio bytes to a temporary file for processing
            with open("temp_audio.wav", "wb") as temp_audio_file:
                temp_audio_file.write(user_audio_data)
            
            user_text = process_user_input("temp_audio.wav")
            applicant_chat(applicant_id, f"Applicant: {user_text}")

            ai_message = await process_applicant(applicant, applicant.resume)  # Replace with AI response generation logic
            if isinstance(ai_message, str):
                await websocket.send_text(ai_message)
            else:
                await websocket.send_text(f"Error: {ai_message}")
    except WebSocketDisconnect:
        applicant_chat(applicant_id, "Interview ended")
