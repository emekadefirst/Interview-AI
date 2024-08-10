import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Applicant, InterviewConversation
from service import service
from sessions import (
    create_applicant,
    all_applicant,
    applicant_by_id,
    all_applicant_chat
)

app = FastAPI(
    title="Interview AI",
    description="Interview AI",
    version="0.1.0"
)

app.include_router(service, prefix="/api")

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

    applicant = create_applicant(fullname, role, about, file_path)
    
    return {"message": "Applicant created", "applicant_id": applicant.id}


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

