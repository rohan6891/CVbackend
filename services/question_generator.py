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

async def generate_interview_questions(job_title: str,
                               job_description: str,
                               experience_level: str,
                               competencies: List[str],
                               interview_type: str,
                               resume_info: dict) -> List[str]:
    """
    Strictly formatted interview question generator using Groq.
    Returns raw model output with assumption of perfect compliance.
    """
    prompt = f"""
<INSTRUCTIONS>
You MUST follow these rules IMPLICITLY:
1. Output EXCLUSIVELY a JSON array of exactly 25 strings
2. Use double quotes ONLY
3. No markdown, comments, or text outside the array
4. Strict JSON syntax - no trailing commas
5. Questions must end with . or ?
6. Questions must be specific to these exact requirements:

<JOB_REQUIREMENTS>
Title: {job_title}
Description: {job_description}
Level: {experience_level}
Competencies: {competencies}
Type: {interview_type}

<CANDIDATE_PROFILE>
{json.dumps(resume_info, indent=2)}

<SAMPLE_FORMAT_EXAMPLE>
[
  "How does your experience with {resume_info['skills'][0]} align with our need for {competencies[0]}?",
  "Describe a {experience_level}-level challenge you faced in {job_title} role?",
  "Explain your approach to {job_description.split()[0]} in production environments?"
]

<STRICT_PROHIBITIONS>
- No text outside array
- No array wrappers
- No keys or objects
- No numbered questions
- No extra punctuation
</INSTRUCTIONS>
"""

    messages = [
        {
            "role": "system",
            "content": ("You are a JSON array syntax enforcer. You must output "
                       "EXCLUSIVELY a JSON array of 25 to 50 question strings with "
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
        raise Exception(f"Failed to generate questions: {str(e)}")

async def calculate_matching_score(
    job_requirements: dict,
    candidate_profile: dict
) -> dict:
    """Calculate matching score with 3 key metrics using Groq"""
    prompt = f"""
<INSTRUCTIONS>
Analyze ONLY these 3 match factors and return STRICTLY:
1. overall_match: Percentage (0-100) of overall match
2. skill_match: Percentage (0-100) of required skills match
3. experience_match: Percentage (0-100) of experience level match

Output MUST be JSON with ONLY these 3 keys. No explanations. No markdown.

<JOB_REQUIREMENTS>
{json.dumps(job_requirements, indent=2)}

<CANDIDATE_PROFILE>
{json.dumps(candidate_profile, indent=2)}

<EXAMPLE_RESPONSE>
{{"overall_match":90,
  "skill_match": 85,
  "experience_match": 90,
}}
</INSTRUCTIONS>
"""

    messages = [
        {
            "role": "system",
            "content": "You are a scoring machine. Return ONLY JSON with 3 numeric values."
        },
        {"role": "user", "content": prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=150,
            response_format={"type": "json_object"},
            stream=False
        )
        
        return json.loads(completion.choices[0].message.content.strip())
    except Exception as e:
        raise Exception(f"Scoring error: {str(e)}")