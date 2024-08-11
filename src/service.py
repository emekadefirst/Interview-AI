import os
import tempfile
from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import pdfplumber


service = APIRouter()


load_dotenv()


try:
    import google.generativeai as genai
    print("Successfully imported required libraries")
    genai.configure(api_key=os.environ.get('gemini_api'))
    model = genai.GenerativeModel('gemini-1.5-pro')
except ImportError as e:
    print(f"Failed to import libraries: {e}")
    raise


AUDIO_FOLDER = 'audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

class ApplicantInfo(BaseModel):
    fullname: str
    about: str
    role: str

def extract_resume_text(resume_file: UploadFile) -> str:
    with pdfplumber.open(resume_file.file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def generate_interview_prompt(applicant: ApplicantInfo, resume_content: str, conversation_history: str = "") -> str:
    base_prompt = f"""
    You are an experienced AI interviewer for TechCorp. Your task is to conduct a professional and thorough interview with {applicant.fullname} for the position of {applicant.role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:

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
    4. Conclude the interview professionally when appropriate.

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
    return base_prompt

async def process_applicant(applicant: ApplicantInfo, resume_content: str, conversation_history: str = ""):
    try:
        prompt = generate_interview_prompt(applicant, resume_content, conversation_history)
        response = model.generate_content(prompt)
        interview_text = response.text if response.text else "I apologize, but I couldn't generate a response. Let's try again."

        audio_filename = f"{applicant.fullname.replace(' ', '_')}_interview.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        tts = gTTS(text=interview_text, lang='en')
        tts.save(audio_path)

        return {"text": interview_text, "audio_path": audio_path, "audio_filename": audio_filename}

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}

@service.post("/apply")
async def apply_for_job(
    fullname: str,
    role: str,
    about: str,
    resume: UploadFile = File(...)
):
    try:
        applicant = ApplicantInfo(fullname=fullname, role=role, about=about)
        resume_content = extract_resume_text(resume)
        
        conversation_history = ""

        
        result = await process_applicant(applicant, resume_content, conversation_history)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        
        return JSONResponse(content={
            "text": result["text"],
            "audio_url": f"http://127.0.0.1:8000/apply/audio/{result['audio_filename']}"
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@service.get("/apply/audio/{filename}")
async def get_audio_file(filename: str):
    try:
        audio_path = os.path.join(AUDIO_FOLDER, filename)
        if not os.path.isfile(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        return StreamingResponse(open(audio_path, "rb"), media_type="audio/mp3")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
