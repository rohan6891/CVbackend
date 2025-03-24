from pydantic import BaseModel
from typing import List, Optional

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class JobDetails(BaseModel):
    job_title: str
    job_description: str
    experience_level: str
    competencies: List[str]
    interview_type: str

class HistoryEntry(BaseModel):
    user_email: str
    job_title: str
    job_id: str
    date: str
    action: str