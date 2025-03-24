from groq import Groq
import json
from typing import Any, Dict, List
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from docx import Document
import io
import os
import re
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DETAILED_RESUME_TEMPLATE = {
    "personal_information": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1 (123) 456-7890",
        "address": "123 Main St, City, Country",
        "linkedin": "linkedin.com/in/johndoe",
        "portfolio": "johndoe.com"
    },
    "professional_summary": "Experienced software developer...",
    "work_experience": [
        {
            "job_title": "Senior Software Engineer",
            "company": "Tech Corp Inc.",
            "location": "New York, NY",
            "dates": "03/2018 - Present",
            "responsibilities": [
                "Lead team of 5 developers",
                "Architected cloud-based solutions"
            ],
            "achievements": [
                "Reduced system latency by 40%",
                "Implemented CI/CD pipeline"
            ],
            "technologies_used": ["Python", "AWS", "Docker"]
        }
    ],
    "education": [
        {
            "degree": "Master of Science in Computer Science",
            "institution": "Stanford University",
            "dates": "09/2014 - 06/2016",
            "gpa": "3.8/4.0",
            "honors": ["Summa Cum Laude", "Dean's List"],
            "relevant_coursework": [
                "Advanced Algorithms",
                "Distributed Systems"
            ]
        }
    ],
    "technical_skills": {
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["Django", "React"],
        "tools": ["Git", "Docker"],
        "certifications": [
            "AWS Certified Solutions Architect",
            "Google Cloud Professional"
        ]
    },
    "projects": [
        {
            "name": "E-commerce Platform",
            "description": "Built scalable online marketplace",
            "role": "Full-stack Developer",
            "technologies": ["Python", "React", "PostgreSQL"],
            "dates": "2022-2023",
            "outcomes": "Increased conversion by 25%"
        }
    ],
    "publications": [
        {
            "title": "Machine Learning Optimization",
            "journal": "IEEE Transactions",
            "date": "2020"
        }
    ],
    "languages": [
        {"language": "English", "proficiency": "Native"},
        {"language": "Spanish", "proficiency": "Intermediate"}
    ],
    "volunteer_experience": [
        {
            "organization": "Code for America",
            "role": "Volunteer Developer",
            "dates": "2019-2020"
        }
    ]
}

async def get_resume_summary(text: str) -> Dict[str, Any]:
    prompt = f"""
<INSTRUCTIONS>
Generate COMPREHENSIVE resume JSON with ALL DETAILS from the content below.

STRICT REQUIREMENTS:
1. Use EXACTLY this structure:
{json.dumps(DETAILED_RESUME_TEMPLATE, indent=2)}
2. Follow these rules:
   - Dates: "MM/YYYY - MM/YYYY" or "Present" for current positions
   - Phone: International format "+X XXX XXX XXXX"
   - Sort education by completion date DESC
   - Include MINIMUM 3 bullet points for responsibilities/achievements
   - Extract ALL technologies/tools mentioned
   - Preserve exact company/project names
   - Include GPA if available
   - Convert all dates to consistent format

PROHIBITIONS:
- No missing sections
- No markdown formatting
- No truncated information
- No placeholder values
- No text outside JSON

<RESUME_CONTENT>
{text}
</RESUME_CONTENT>
"""

    messages = [
        {
            "role": "system",
            "content": "You are a senior HR analyst. Extract COMPLETE resume details with maximum fidelity."
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Resume parsing failed: {str(e)}")
    

async def parse_resume(file: Any) -> Dict[str, Any]:
    """Strict resume parser with direct processing"""
    file_content = await file.read()
    
    if file.filename.lower().endswith('.pdf'):
        text = '\n'.join(
            p.extract_text() 
            for p in PdfReader(io.BytesIO(file_content)).pages
            if p.extract_text()
        )
    elif file.filename.lower().endswith('.docx'):
        text = '\n'.join(
            p.text 
            for p in Document(io.BytesIO(file_content)).paragraphs
            if p.text
        )
    else:
        raise ValueError("Only PDF/DOCX supported")
    
    return await get_resume_summary(text)


JOB_DESCRIPTION_TEMPLATE = {
    "job_title": "Software Engineer",
    "company": "Tech Innovations Inc.",
    "location": "San Francisco, CA",
    "employment_type": "Full-time",
    "experience_level": "Mid-level",
    "required_skills": ["Python", "Django", "AWS"],
    "preferred_skills": ["React", "Docker"],
    "responsibilities": [
        "Develop and maintain web applications",
        "Collaborate with cross-functional teams",
        "Optimize system performance"
    ],
    "qualifications": {
        "education": "Bachelor’s degree in Computer Science or related field",
        "experience_years": "3-5 years",
        "certifications": ["AWS Certified Developer"]
    },
    "description": "We are seeking a skilled Software Engineer to join our dynamic team..."
}

async def get_job_description_summary(text: str) -> Dict[str, Any]:
    prompt = f"""
<INSTRUCTIONS>
Generate a COMPREHENSIVE job description JSON with ALL DETAILS from the content below.

STRICT REQUIREMENTS:
1. Use EXACTLY this structure:
{json.dumps(JOB_DESCRIPTION_TEMPLATE, indent=2)}
2. Follow these rules:
   - Extract the exact job title and company name if provided
   - Identify location (city, state, country) if mentioned, otherwise use "Not specified"
   - Employment type: "Full-time", "Part-time", "Contract", "Internship", or "Not specified"
   - Experience level: "Entry-level", "Mid-level", "Senior", "Executive", or "Not specified" (infer from context if not explicit)
   - Split skills into "required_skills" (mandatory) and "preferred_skills" (optional/nice-to-have); list ALL mentioned technologies/tools
   - Responsibilities: Minimum 3 bullet points; infer from text if needed
   - Qualifications: Include education, experience years (e.g., "3-5 years"), and certifications if mentioned
   - Preserve the full raw text in "description"
   - Use "Not specified" for any missing fields unless inferable

PROHIBITIONS:
- No missing sections
- No markdown formatting
- No truncated information
- No placeholder values beyond "Not specified"
- No text outside JSON

<JOB_DESCRIPTION_CONTENT>
{text}
</JOB_DESCRIPTION_CONTENT>
"""

    messages = [
        {
            "role": "system",
            "content": "You are a senior job analyst. Extract COMPLETE job description details with maximum fidelity."
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Job description parsing failed: {str(e)}")

# Example usage
async def parse_job_description(job_text: str) -> Dict[str, Any]:
    """Parse job description text into structured JSON."""
    return await get_job_description_summary(job_text)