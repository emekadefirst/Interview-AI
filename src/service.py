import os
import io
import speech_recognition as sr
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sessions import applicant_by_id
from fastapi import UploadFile, Form
import speech_recognition as sr
from typing import Union, IO
from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from gtts import gTTS
import pdfplumber
import google.generativeai as genai

service = APIRouter()

load_dotenv()
try:
    genai.configure(api_key=os.environ.get('gemini_api'))
    model = genai.GenerativeModel('gemini-1.5-pro')
except ImportError as e:
    print(f"Failed to import libraries: {e}")
    raise

AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

RESUME_FOLDER = 'resumes'
os.makedirs(RESUME_FOLDER, exist_ok=True)

class ApplicantInfo(BaseModel):
    fullname: str
    about: str
    role: str   
    



def extract_resume_text(resume_file_path: str) -> str:
    with pdfplumber.open(resume_file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

"""user audio response"""
def convert_audio_to_text(audio_input: Union[str, IO]) -> str:
    recognizer = sr.Recognizer()

    try:
        if isinstance(audio_input, str):
            with sr.AudioFile(audio_input) as source:
                audio_data = recognizer.record(source)
        elif isinstance(audio_input, IO):
            with sr.AudioFile(audio_input) as source:
                audio_data = recognizer.record(source)
            return "Invalid input type. Must be a file path or a file-like object."

        text = recognizer.recognize_google(audio_data)
        return text

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
    Your name is InAS, you are an experienced conversational AI interviewer for Tech company. Your task is to conduct a professional and thorough interview with {applicant.fullname} for the position of {applicant.role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:
    What wherever Tech stack or {applicant.role} they claim to be leverage on your descrection to ask industry based question like that of leetcode.
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
    4. Test their problem solving ability
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
        ai_response = interview_text.replace("## Interviewer", "").strip()
        cleaned_text = ai_response.replace('"', '').strip()

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


  


@service.post("interview/{applicant_id}")
async def interview(applicant_id: int):
    fetch = applicant_by_id(applicant_id)
    read = extract_resume_text(fetch['resume'])  # assuming fetch['resume'] is the file path
    applicant = ApplicantInfo(fullname=fetch['fullname'], role=fetch['role'], about=fetch['about'])
    conversation_history = ""  # Initialize empty conversation history
    response = process_applicant(applicant, read, conversation_history)
    
    # Return initial text and audio response
    return JSONResponse(content={
        "text": response['text'],
        "audio_url": f"http://127.0.0.1:8000/apply/audio/{response['audio_filename']}"
    })

@service.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    query_params = websocket.query_params
    applicant_id = query_params.get('applicant_id')

    try:
        conversation_history = ""
        while True:
            audio_data = await websocket.receive_bytes()
            r = sr.Recognizer()
            audio = sr.AudioFile(io.BytesIO(audio_data))  
            with audio as source:
                audio_content = r.record(source)
            text_in = r.recognize_google(audio_content) 
            conversation_history += f"User: {text_in}\n"

            # Use the applicant_id to fetch the applicant data
            fetch = applicant_by_id(applicant_id)
            applicant_info = ApplicantInfo(
                fullname=fetch['fullname'], 
                role=fetch['role'], 
                about=fetch['about']
            )

            # Process the conversation
            response = process_applicant(applicant_info, None, conversation_history)
            conversation_history += f"AI: {response['text']}\n"
            
            await websocket.send_json({
                "text": response['text'],
                "audio_url": f"http://127.0.0.1:8000/apply/audio/{response['audio_filename']}"
            })
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
