import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine


load_dotenv()

def create_db():
    # db_url = os.environ.get('postresql_url')
    # if db_url is None:
    #     raise ValueError("PostgreSQL URL not found in environment variables")
    # print(f"Database URL: {db_url}") 
    db_name = "ai.db"
    db_url = f"sqlite:///{db_name}" 
    engine = create_engine(db_url, echo=True)
    SQLModel.metadata.create_all(engine)
    return engine

engine = create_db()