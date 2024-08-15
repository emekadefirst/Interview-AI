from sqlmodel import Session, select
from .models import Applicant, InterviewSummary, Interview_session
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
def chat_history(messages, applicant_code):
    with Session(engine) as session:
        data = Interview_session(messages=messages, applicant_code=applicant_code)
        session.add(data)
        session.commit()
        return "Chat History"

def get_chat_history(applicant_code):
    with Session(engine) as session:
        statement = select(Interview_session).where(Interview_session.applicant == applicant_code)
        results = session.exec(statement).all()
        return results

def applicant_summary(code, summary):
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
