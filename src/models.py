from datetime import datetime
from sqlmodel import SQLModel, Field
from database import create_db

class Applicant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fullname: str = Field(index=True)
    role: str
    about : str
    resume: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewConversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    applicant: int = Field(foreign_key="applicant.id")
    interview_result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __str__(self):
        return "Applicant Interview detail with ai"

create_db()