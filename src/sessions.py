from sqlmodel import Session, select
from .models import Applicant, InterviewSummary, InterviewSession
from .database import engine

# Create a new applicant
def create_applicant(fullname, role, about, resume):
    with Session(engine) as session:
        data = Applicant(fullname=fullname, role=role, about=about, resume=resume)
        session.add(data)
        session.commit()
        session.refresh(data)
        response = {"interview_id": data.code}
        return response

# Retrieve all applicants
def all_applicants():
    with Session(engine) as session:
        statement = select(Applicant)
        applications = session.exec(statement).all()
        return applications

# Retrieve an applicant by their unique code
def applicant_by_code(applicant_code):
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

# Store chat history
def chat_history(messages, applicant_code):
    with Session(engine) as session:
        data = InterviewSession(chat=messages, applicant_code=applicant_code)
        session.add(data)
        session.commit()
        return "Chat History stored successfully"

# Retrieve chat history by applicant code
def get_chat_history(applicant_code):
    with Session(engine) as session:
        statement = select(InterviewSession).where(InterviewSession.applicant_code == applicant_code)
        results = session.exec(statement).all()
        return results

# Store interview summary for an applicant
def applicant_summary(applicant_code, summary):
    with Session(engine) as session:
        data = InterviewSummary(applicant_code=applicant_code, interview_result=summary)
        session.add(data)
        session.commit()
        return "Summary of Interview stored successfully"

# Retrieve all interview summaries
def all_summaries():
    with Session(engine) as session:
        statement = select(InterviewSummary)
        summaries = session.exec(statement).all()
        return summaries

# Retrieve interview summary by applicant code
def summary_by_code(applicant_code):
    with Session(engine) as session:
        statement = select(InterviewSummary).where(InterviewSummary.applicant_code == applicant_code)
        response = session.exec(statement).one_or_none()
        return response
