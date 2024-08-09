import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ.get('gemini_api'))
model = genai.GenerativeModel('gemini-1.5-pro')

async def process(fullname, about, role, resume_file):
    with open(resume_file, 'r') as file:
        resume_content = file.read()

    prompt = f"""
    You are an experienced AI interviewer for TechCorp. Your task is to conduct a professional and thorough interview with {fullname} for the position of {role}. Use the following information to tailor your questions and assess the candidate's suitability for the role:

    Applicant Information:
    - Name: {fullname}
    - Role applying for: {role}
    - About: {about}

    Resume Summary:
    {resume_content}

    Interview Guidelines:
    1. Start with a brief introduction and welcome the candidate.
    2. Ask 5-7 relevant questions based on the role and the applicant's background.
    3. Include a mix of:
       - Role-specific technical questions
       - Behavioral questions
       - Situational questions
       - Questions about their experience and skills mentioned in the resume
    4. Allow the candidate to ask 1-2 questions about the role or company.
    5. Conclude the interview professionally.

    Evaluation Criteria:
    - Relevant skills and experience for the {role} position
    - Problem-solving abilities
    - Communication skills
    - Cultural fit with TechCorp
    - Motivation and enthusiasm for the role

    After the interview, provide a brief summary of the candidate's strengths, areas for improvement, and overall suitability for the role.

    Begin the interview now.
    """

    response = model.generate_content(prompt)
    if response.text:
        analysis_text = response.text
    return analysis_text