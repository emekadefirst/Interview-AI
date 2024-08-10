from sqlmodel import Session, select
from models import Applicant, InterviewConversation
from database import engine

def create_applicant(fullname, role, about, resume):
    with Session(engine) as session:
        data = Applicant(fullname=fullname, role=role, about=about, resume=resume)
        session.add(data)
        session.commit()
        return "Applicant created"
def all_applicant():
    with Session(engine) as session:
        statement = select(Applicant)
        application = session.exec(statement).all()
        return application

def applicant_by_id(applicant_id):
    with Session(engine) as session:
        statement = select(Applicant).where(Applicant.id == applicant_id)
        response = session.exec(statement).one_or_none()
        return response

"""Chat"""  
def applicant_chat(id, response):
    with Session(engine) as session:
        data = InterviewConversation(applicant=id, interview_result=response)
        session.add(data)
        session.commit()
        return "Applicant created"
def all_applicant_chat():
    with Session(engine) as session:
        statement = select(InterviewConversation)
        application = session.exec(statement).all()
        return application

# def applicant_info_by_id(applicant_id):
#     with Session(engine) as session:
#         statement = select(InterviewConversation).where(InterviewConversation.id == applicant_id)
#         response = session.exec(statement).one_or_none()
#         return response
