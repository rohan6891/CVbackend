import uuid
from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from services.question_generator import generate_interview_questions, calculate_matching_score
from services.resume_parser import parse_resume
from database import history_collection
from datetime import datetime

router = APIRouter()

@router.post("/generate_questions")
async def generate_questions(
    
    user_email: str = Form(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    experience_level: str = Form(...),
    competencies: str = Form(...),
    interview_type: str = Form(...),
    candidate_resume: UploadFile = File(...)
):
    try:
        # Parse competencies and resume
        competencies_list = [c.strip() for c in competencies.split(",")]
        resume_info = await parse_resume(candidate_resume)
        
        # Calculate matching score
        job_requirements = {
            "title": job_title,
            "description": job_description,
            "experience_level": experience_level,
            "competencies": competencies_list,
            "interview_type": interview_type
        }
        
        match_score = await calculate_matching_score(job_requirements, resume_info)
        
        # Generate questions
        questions = await generate_interview_questions(
            job_title,
            job_description,
            experience_level,
            competencies_list,
            interview_type,
            resume_info
        )
        
        if isinstance(questions, dict):
            raise HTTPException(status_code=500, detail=questions.get("error"))
        
        job_id = str(uuid.uuid4())
        
        # Create history entry
        history_entry = {
            "job_id": job_id,
            "user_email": user_email,
            "job_title": job_title,
            "job_description": job_description,
            "experience_level": experience_level,
            "competencies": competencies_list,
            "interview_type": interview_type,
            "questions": questions,
            "candidate_info": resume_info,
            "match_score": match_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await history_collection.insert_one(history_entry)
        
        return {
            "job_id": job_id,
            "questions": questions,
            "candidate_info": resume_info,
            "match_score": match_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        candidate_resume.file.close()
