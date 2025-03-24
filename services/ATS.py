from datetime import datetime
from groq import Groq
import os
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

async def calculate_matching_score(
    job_requirements: dict,
    candidate_profile: dict
) -> dict:
    """Calculate comprehensive matching score with frontend-ready data"""
    prompt = f"""
<INSTRUCTIONS>
Analyze the match between job requirements and candidate profile. Return JSON with:
1. overall_match: Overall match percentage (0-100)
2. skill_match: Skills match percentage (0-100)
3. experience_match: Experience match percentage (0-100)
4. score_breakdown: List of specific skill matches
5. missing_skills: List of missing required skills
6. experience_gap: String describing experience difference
7. match_analysis: Brief summary of strengths/gaps (50 words max)

Use this structure:
{{
  "overall_match": number,
  "skill_match": number,
  "experience_match": number,
  "score_breakdown": [{{"skill": string, "match": number}}],
  "missing_skills": [string],
  "experience_gap": string,
  "match_analysis": string
}}

<JOB_REQUIREMENTS>
{json.dumps(job_requirements, indent=2)}

<CANDIDATE_PROFILE>
{json.dumps(candidate_profile, indent=2)}

<EXAMPLE>
{{
  "overall_match": 85,
  "skill_match": 90,
  "experience_match": 80,
  "score_breakdown": [
    {{"skill": "Python", "match": 95}},
    {{"skill": "AWS", "match": 85}},
    {{"skill": "React", "match": 75}}
  ],
  "missing_skills": ["Docker", "Kubernetes"],
  "experience_gap": "Candidate has 4 years vs required 5+ years",
  "match_analysis": "Strong core skills match but missing some DevOps tools. Slightly below required experience level but shows relevant project history."
}}
</INSTRUCTIONS>
"""

    messages = [
        {
            "role": "system",
            "content": "You are a career matching analyst. Return structured JSON with scores and detailed breakdown for UI display."
        },
        {"role": "user", "content": prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Groq-optimized model
            messages=messages,
            temperature=0.2,
            max_tokens=400,
            response_format={"type": "json_object"},
            stream=False
        )
        
        response = json.loads(completion.choices[0].message.content.strip())
        
        # Add source metadata for frontend
        response.update({
            "job_id": job_requirements.get("id"),
            "candidate_id": candidate_profile.get("id"),
            "calculation_date": datetime.utcnow().isoformat()
        })
        
        return response
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Scoring error: {str(e)}")