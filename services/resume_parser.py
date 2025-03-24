from groq import Groq
import json
from typing import Any, Dict
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from docx import Document
import io
import os
import re

load_dotenv()
# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

RESUME_TEMPLATE = {
    "candidate_name": "John Doe",
    "contact_info": {"email": "john@example.com", "phone": "123-456-7890"},
    "skills": ["Python", "Project Management"],
    "experience_years": 5,
    "education": ["Bachelor's in Computer Science"],
    "work_history": ["Software Engineer at XYZ Corp"],
    "achievements": ["Increased efficiency by 20%"],
    "professional_summary": "Experienced software developer...",
    "core_competencies": ["Software Development", "Team Leadership"]
}

async def get_resume_summary(text: str) -> Dict[str, Any]:
    """
    Strictly formatted resume parser using Groq
    """
    prompt = f"""
<INSTRUCTIONS>
You MUST:
1. Output EXCLUSIVELY a JSON object matching this EXACT structure:
{json.dumps(RESUME_TEMPLATE, indent=2)}
NOTE: the values are placeholders and should be replaced with the actual resume data.
2. Use double quotes ONLY
3. Maintain all keys exactly as shown
4. Never include markdown or extra text
5. Follow these value rules:
   - experience_years: integer only
   - phone: "xxx-xxx-xxxx" format or empty string
   - skills: minimum 5 items
   - education: array of strings
6.In the education array, keep the array in a sorted order on the basis of year of completion DESCENDING ORDER.

<PROHIBITIONS>
- No text outside JSON object
- No missing keys
- No schema deviations
- No comments
- No trailing commas

<RESUME_CONTENT>
{text} 
</INSTRUCTIONS>
"""

    messages = [
        {
            "role": "system", 
            "content": "You are a JSON schema validator. Return ONLY perfect JSON matching the exact template."
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False
        )
        
        response_content = completion.choices[0].message.content.strip()
        return json.loads(response_content)
    except Exception as e:
        raise Exception(f"Failed to parse resume: {str(e)}")

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

# File extraction helpers remain unchanged but should be simplified similarly
# Remove all text cleaning and normalization
# Assume model can handle raw extracted text