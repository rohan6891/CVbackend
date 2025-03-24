from groq import Groq
from dotenv import load_dotenv
import os
import json
from typing import List

# Load environment variables
load_dotenv()

# Initialize Groq client with API key from environment variables
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

async def generate_interview_answers(job_title: str,
                                     job_description: str,
                                     experience_level: str,
                                     competencies: List[str],
                                     interview_type: str,
                                     resume_info: dict,
                                     questions: List[str]) -> List[str]:
    """
    Generate answers for the given interview questions using Groq.
    Returns raw model output with assumption of perfect compliance.
    """
    prompt = f"""
<INSTRUCTIONS>
You MUST follow these rules IMPLICITLY:
1. Output EXCLUSIVELY a JSON array of strings, each representing an answer to the corresponding question.
2. Use double quotes ONLY
3. No markdown, comments, or text outside the array
4. Strict JSON syntax - no trailing commas
5. Answers must be specific to these exact requirements:
6. Answer must be brief, relevant, and professional and should not be like a one word answer.

<JOB_REQUIREMENTS>
Title: {job_title}
Description: {job_description}
Level: {experience_level}
Competencies: {competencies}
Type: {interview_type}

<CANDIDATE_PROFILE>
{json.dumps(resume_info, indent=2)}

<QUESTIONS>
{json.dumps(questions, indent=2)}

<SAMPLE_FORMAT_EXAMPLE>
Only for FORMAT reference
[
  "I have extensive experience with {resume_info['skills'][0]}, which aligns well with your need for {competencies[0]}.",
  "In my previous role as a {job_title}, I faced a {experience_level}-level challenge where I...",
  "My approach to {job_description.split()[0]} in production environments involves..."
]

<STRICT_PROHIBITIONS>
- No text outside array
- No array wrappers
- No keys or objects
- No numbered answers
- No extra punctuation
</INSTRUCTIONS>
"""

    messages = [
        {
            "role": "system",
            "content": ("You are a JSON array syntax enforcer. You must output "
                       "EXCLUSIVELY a JSON array of answer strings with "
                       "perfect syntax and zero additional text.")
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
        
        raw_response = completion.choices[0].message.content.strip()
        return json.loads(raw_response)
    except Exception as e:
        raise Exception(f"Failed to generate answers: {str(e)}")