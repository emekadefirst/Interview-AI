from pydantic import BaseModel


class ApplicantCreate(BaseModel):
    fullname: str
    role: str
    about: str
    resume: str
    release_date: str