from sqlmodel import Session, select
from .models import Applicant, InterviewSummary
from .database import engine

def create_applicant(fullname, role, about, resume):
    with Session(engine) as session:
        data = Applicant(fullname=fullname, role=role, about=about, resume=resume)
        session.add(data)
        session.commit()
        session.refresh(data)
        response = {"interview_id": data.code }  
        return response

def all_applicant():
    with Session(engine) as session:
        statement = select(Applicant)
        application = session.exec(statement).all()
        return application

def applicant_by_id(applicant_code):
    with Session(engine) as session:
        statement = select(Applicant).where(Applicant.code == applicant_code)
        response = session.exec(statement).one_or_none()

        if response:
            return {
                "fullname": response.fullname,
                "role": response.role,
                "about": response.about,
                "resume": response.resume
            }
        return None


"""Chat"""  
def applicant_chat(code, summary):
    with Session(engine) as session:
        data = InterviewSummary(applicant=code, interview_result=summary)
        session.add(data)
        session.commit()
        return "Summary of Interview"

def all_applicant():
    with Session(engine) as session:
        statement = select(InterviewSummary)
        summary = session.exec(statement).all()
        return summary

def applicant_by_id(applicant_code):
    with Session(engine) as session:
        statement = select(InterviewSummary).where(InterviewSummary.code == applicant_code)
        response = session.exec(statement).one_or_none()
        return response
