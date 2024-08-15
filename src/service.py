import os
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile, APIRouter, HTTPException, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from .sessions import *
import speech_recognition as sr
from typing import Union, IO
from dotenv import load_dotenv
from gtts import gTTS
import pdfplumber
import google.generativeai as genai

service = APIRouter()

load_dotenv()

try:
    genai.configure(api_key=os.environ.get('gemini_api'))
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    print(f"Failed to configure Generative AI: {e}")
    raise

AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

RESUME_FOLDER = 'resumes'
os.makedirs(RESUME_FOLDER, exist_ok=True)

service.mount("/apply/audio", StaticFiles(directory=AUDIO_FOLDER), name="audio")

class ApplicantInfo(BaseModel):
    fullname: str
    about: str
    role: str

# Conversation history storage
conversation_histories = {}

def extract_resume_text(resume_file_path: str) -> str:
    try:
        with pdfplumber.open(resume_file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting resume text: {str(e)}")

def convert_audio_to_text(audio_input: Union[str, IO]) -> str:
    recognizer = sr.Recognizer()
    try:
        if isinstance(audio_input, str):
            with sr.AudioFile(audio_input) as source:
                audio_data = recognizer.record(source)
        elif isinstance(audio_input, IO):
            with sr.AudioFile(audio_input) as source:
                audio_data = recognizer.record(source)
        else:
            return "Invalid input type. Must be a file path or a file-like object."

        return recognizer.recognize_google(audio_data)

    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"An error occurred: {e}"

def generate_interview_prompt(applicant: ApplicantInfo, resume_content: str, conversation_history: str = "") -> str:
    return f"""
    Your name is InAS, you are an experienced conversational AI interviewer for Our Company. Your task is to conduct a professional and thorough interview with {applicant.fullname} for the position of {applicant.role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:
    What whatever Tech stack or {applicant.role} they claim to be leverage on your discretion to ask industry-based questions like that of leetcode.
    Applicant Information:
    - Name: {applicant.fullname}
    - Role applying for: {applicant.role}
    - About: {applicant.about}

    Resume Summary:
    {resume_content}

    Interview Guidelines:
    1. Start with a brief introduction and welcome the candidate.
    2. Ask relevant questions based on the role and the applicant's background.
       - Include a mix of:
         - Role-specific technical questions
         - Behavioral questions
         - Situational questions
         - Questions about their experience and skills mentioned in the resume
    3. Allow the candidate to ask questions about the role or company.
    4. Test their problem-solving ability
    5. Conclude the interview professionally when appropriate.

    Evaluation Criteria:
    - Relevant skills and experience for the {applicant.role} position
    - Problem-solving abilities
    - Communication skills
    - Cultural fit with TechCorp
    - Motivation and enthusiasm for the role

    Conversation History:
    {conversation_history}

    Please provide the next question or response in the interview process.
    """

def process_applicant(applicant: ApplicantInfo, resume_content: str, conversation_history: str = ""):
    try:
        prompt = generate_interview_prompt(applicant, resume_content, conversation_history)
        response = model.generate_content(prompt)

        interview_text = response.text if response.text else "I apologize, but I couldn't generate a response. Let's try again."
        cleaned_text = interview_text.replace("## InAS (Interviewer):", "").strip().replace('"', '')

        audio_filename = f"{applicant.fullname.replace(' ', '_')}_interview.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        tts = gTTS(text=cleaned_text, lang='en')
        tts.save(audio_path)

        return {
            "text": cleaned_text,
            "audio_path": audio_path,
            "audio_filename": audio_filename
        }

    except Exception as e:
        return {
            "error": f"Internal server error: {str(e)}",
            "text": "",
            "audio_path": "",
            "audio_filename": ""
        }

@service.post("/interview/{applicant_code}")
async def interview(applicant_code: str, audio: UploadFile = File(None)):
    fetch = applicant_by_id(applicant_code)
    if fetch is None:
        return JSONResponse(content={"error": "Applicant not found"}, status_code=404)
    
    resume_content = extract_resume_text(fetch['resume'])
    applicant = ApplicantInfo(fullname=fetch['fullname'], role=fetch['role'], about=fetch['about'])
    conversation_history = conversation_histories.get(applicant_code, "")
    
    response = process_applicant(applicant, resume_content, conversation_history)
    
    if response.get("error"):
        return JSONResponse(content={"error": response["error"]}, status_code=500)
    
    if response.get("text") and response.get("audio_filename"):
        conversation_histories[applicant_code] = response["text"]
        return JSONResponse(content={
            "text": response['text'],
            "audio_url": f"http://127.0.0.1:8000/apply/audio/{response['audio_filename']}"
        })

    if audio:
        audio_content = await audio.read()
        audio_filename = f"{applicant_code}_{audio.filename}"
        audio_file_path = os.path.join(AUDIO_FOLDER, audio_filename)
        with open(audio_file_path, 'wb') as audio_file:
            audio_file.write(audio_content)

        user_response_text = convert_audio_to_text(audio_file_path)
        conversation_histories[applicant_code] = user_response_text
        
        return JSONResponse(content={
            "text": user_response_text,
            "audio_url": f"http://127.0.0.1:8000/apply/audio/{audio_filename}"
        })
    
    return JSONResponse(content={"error": "No response generated"}, status_code=400)

@service.get("/apply/audio/{filename}")
async def get_audio(filename: str):
    audio_path = os.path.join(AUDIO_FOLDER, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path)

@service.websocket("/interview/{applicant_code}")
async def interview_room(websocket: WebSocket, applicant_code: str):
    await websocket.accept()
    try:
        fetch = applicant_by_id(applicant_code)
        resume_content = extract_resume_text(fetch['resume'])
        applicant = ApplicantInfo(fullname=fetch['fullname'], role=fetch['role'], about=fetch['about'])
        conversation_history = conversation_histories.get(applicant_code, "")
        initial_response = process_applicant(applicant, resume_content, conversation_history)
        conversation_histories[applicant_code] = conversation_history + "\nAI: " + initial_response['text']

        await websocket.send_json({
            "text": initial_response['text'],
            "audio_url": f"http://127.0.0.1:8000/apply/audio/{initial_response['audio_filename']}"
        })

        while True:
            audio_input = await websocket.receive_bytes()
            
            audio_temp_path = f"/mnt/data/temp_{applicant_code}.wav"
            with open(audio_temp_path, "wb") as audio_file:
                audio_file.write(audio_input)
            
            user_input_text = convert_audio_to_text(audio_temp_path)
            
            response = process_applicant(applicant, resume_content, conversation_histories[applicant_code])
            
            conversation_histories[applicant_code] += "\nUser: " + user_input_text + "\nAI: " + response['text']
            
            await websocket.send_json({
                "text": response['text'],
                "audio_url": f"http://127.0.0.1:8000/apply/audio/{response['audio_filename']}"
            })

    except WebSocketDisconnect:
        full_conversation = conversation_histories.get(applicant_code, "")
        summary = generate_interview_summary(full_conversation)
        store_interview_summary(applicant_code, summary)
        return "WebSocket disconnected"

def generate_interview_summary(conversation):
    prompt = f"""
    Based on the following interview conversation, please provide a concise summary 
    highlighting the key points discussed, the candidate's strengths and weaknesses, 
    and an overall assessment of their suitability for the role:

    {conversation}

    Please structure the summary as follows:
    1. Key Points Discussed
    2. Candidate's Strengths
    3. Areas for Improvement
    4. Overall Assessment
    """
    response = model.generate_content(prompt)
    return response.text

def store_interview_summary(applicant_code, summary):
    chat_history(summary, applicant_code)