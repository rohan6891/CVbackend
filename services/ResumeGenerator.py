import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
import json
from typing import Dict, Any, Optional
from fastapi import Form

current_dir = os.path.dirname(os.path.abspath(__file__))
# Set Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/rohan6891/Desktop/projects/cvcraft/backend/app/services/service.json"

# Initialize AI Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=GenerationConfig(
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=8192,
    )
)

async def generate_enhanced_resume(
    parsed_resume: Dict[str, Any],
    template_file: str,
    job_description: Optional[str] = Form(None),
    additional_info: str = ""
) -> Dict[str, str]:

    print("in generate_enhanced_resume")
    print(parsed_resume)
    print(job_description)
    print(template_file)
    print(additional_info)


    with open(f"templates/{template_file}", "r") as f:
        template_content = f.read()
        print(template_content)

    generation_prompt = f"""
    Generate 100% compilable LaTeX code for a resume strictly based on the provided data and template:

    --- ETHICAL GUIDELINES ---
    - Use ONLY data from resume_data and additional_info.
    - DO NOT fabricate any information.
    - Tailor content specifically to the job_description.

    --- TEMPLATE INSTRUCTIONS ---
    - Preserve the provided template's preamble and styling commands exactly once.
    - Populate the template's existing sections (Education, Experience, etc.) with resume_data.
    - Create new sections if needed (Certifications, Projects, etc.) following template styling.

    --- FORMATTING RULES ---
    - Escape LaTeX special characters (&, %, $, #, _, {{, }}).
    - Format lists using itemize.
    - Return JSON: {{"latex_code": "..."}}

    --- RESUME DATA ---
    {json.dumps(parsed_resume, indent=2)}

    --- JOB DESCRIPTION ---
    {json.dumps(job_description, indent=2)}

    --- ADDITIONAL INFO ---
    {additional_info if additional_info.strip() else "None"}
    """
    
    print(generation_prompt)

    # Generate LaTeX code
    response = model.generate_content(generation_prompt)
    response_text = response.text.strip()
    # Log the raw response for debugging
    print("Raw Generation Response:", response_text)

    # Strip markdown backticks and "json" label if present
    if response_text.startswith("```json"):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith("```") and response_text.endswith("```"):
        response_text = response_text[3:-3].strip()

    # Check if the response is empty
    if not response_text:
        raise ValueError("Empty response from AI model.")

    try:
        response_dict = json.loads(response_text)
        latex_code = response_dict["latex_code"]
        print("Generated LaTeX Code:", latex_code)
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Generation JSON parsing failed: {str(e)}. Raw response: {response_text}")

    return {"latex_code": latex_code}