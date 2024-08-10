import os
from fastapi import APIRouter, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from sessions import (

    applicant_by_id,
    applicant_chat,

)
 
service = APIRouter()

try:
    import google.generativeai as genai
    import pdfplumber
    print("Successfully imported google.generativeai")
    load_dotenv()

    genai.configure(api_key=os.environ.get('gemini_api'))
    model = genai.GenerativeModel('gemini-1.5-pro')

    def process(fullname, about, role, resume_file):
        with pdfplumber.open(resume_file) as pdf:
            resume_content = "\n".join([page.extract_text() for page in pdf.pages])

        prompt = f"""
        You are an experienced AI interviewer for TechCorp. Your task is to conduct a professional and thorough interview with {fullname} for the position of {role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:

        Applicant Information:
        - Name: {fullname}
        - Role applying for: {role}
        - About: {about}

        Resume Summary:
        {resume_content}

        Interview Guidelines:
        1. Start with a brief introduction and welcome the candidate.
        2. Ask 5-7 relevant questions based on the role and the applicant's background.
        3. Include a mix of:
        - Role-specific technical questions
        - Behavioral questions
        - Situational questions
        - Questions about their experience and skills mentioned in the resume
        4. Allow the candidate to ask 1-2 questions about the role or company.
        5. Conclude the interview professionally.

        Evaluation Criteria:
        - Relevant skills and experience for the {role} position
        - Problem-solving abilities
        - Communication skills
        - Cultural fit with TechCorp
        - Motivation and enthusiasm for the role

        After the interview, provide a brief summary of the candidate's strengths, areas for improvement, and overall suitability for the role.

        Begin the interview now.
        """

        response = model.generate_content(prompt)
        if response.text:
            return response.text

except ImportError as e:
    print(f"Failed to import: {e}")

if __name__ == "__main__":
    result = process("Victor Chibuogwu Chukwumeka", "I'm an intelligent developer", "Python developer", "cv.pdf")
    print(result)



@service.websocket("/ws/interview/{applicant_id}")
async def websocket_endpoint(websocket: WebSocket, applicant_id: int):
    await websocket.accept()
    try:
        applicant = applicant_by_id(applicant_id)
        if not applicant:
            await websocket.send_text("Applicant not found")
            await websocket.close()
            return
        ai_message = await process(applicant.fullname, applicant.about, applicant.role, applicant.resume, "")
        await websocket.send_text(ai_message)
        applicant_chat(applicant_id, f"AI: {ai_message}")

        while True:
            user_message = await websocket.receive_text()
            applicant_chat(applicant_id, f"Applicant: {user_message}")
            ai_message = await process(applicant.fullname, applicant.about, applicant.role, applicant.resume, user_message)
            await websocket.send_text(ai_message)
            applicant_chat(applicant_id, f"AI: {ai_message}")

    except WebSocketDisconnect:
        applicant_chat(applicant_id, "Interview ended")