import os
import shutil
from typing import Optional
from pydantic import BaseModel
from sessions import create_applicant
from fastapi import APIRouter, HTTPException, File, UploadFile, Form

router = APIRouter()

class ApplicantInfo(BaseModel):
    fullname: str
    about: str
    role: str

RESUME_FOLDER = 'resumes'
os.makedirs(RESUME_FOLDER, exist_ok=True)

@router.post("/create_applicant")
async def create_applicant_endpoint(
    fullname: str = Form(...),
    role: str = Form(...),
    about: str = Form(...),
    resume: Optional[UploadFile] = File(None),
):
    resume_path = None

    if resume:
        resume_path = os.path.join(RESUME_FOLDER, resume.filename)
        try:
            with open(resume_path, "wb") as resume_file:
                shutil.copyfileobj(resume.file, resume_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File error: {str(e)}")

    try:
        new_applicant = create_applicant(fullname=fullname, role=role, about=about, resume=resume_path)
        return new_applicant
    except Exception as e:
        if resume_path and os.path.exists(resume_path):
            os.remove(resume_path)
        raise HTTPException(status_code=500, detail=f"Error creating applicant: {str(e)}")