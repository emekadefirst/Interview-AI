import os
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.models import Applicant, InterviewConversation
from src.sessions import (
    create_applicant,
    all_applicant,
    applicant_by_id,
    applicant_chat,
    all_applicant_chat
)
from src.service import process

app = FastAPI(
    title="Interview AI",
    description="Interview AI",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/application/")
async def upload_resume(
    fullname: str = File(...),
    role: str = File(...),
    about: str = File(...),
    file: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    result = create_applicant(fullname, role, about, file_path)
    
    return {"message": result, "applicant_id": result.id}

@app.get("/applicants/", response_model=List[Applicant])
def get_applicants():
    return all_applicant()

@app.get("/applicant/{applicant_id}", response_model=Applicant)
def get_applicant(applicant_id: int):
    applicant = applicant_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant

@app.get("/interview_results/", response_model=List[InterviewConversation])
def get_interview_results():
    return all_applicant_chat()

@app.websocket("/ws/interview/{applicant_id}")
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