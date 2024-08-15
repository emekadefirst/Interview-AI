from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import os
import uvicorn
import speech_recognition as sr
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models import Applicant
from src.service import service
from src.upload import router
from src.sessions import (
    all_applicant,
    applicant_by_id,
    all_applicant_chat
)

app = FastAPI(
    title="Interview AI",
    description="Interview AI",
    version="0.1.0"
)

app.include_router(service)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def home():
    return "InAs"

@app.get("/applicants/")
def get_applicants():
    return all_applicant()

@app.get("/applicant/{applicant_id}", response_model=Applicant)
def get_applicant(applicant_id: int):
    applicant = applicant_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant

@app.get("/interview_results/")
def get_interview_results():
    return all_applicant_chat()



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
