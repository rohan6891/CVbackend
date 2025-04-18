from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
from services.Parser import parse_job_description, parse_resume
from services.ResumeGenerator import generate_enhanced_resume
import os
from services.LatexCompiler import compile_latex_to_pdf  # Import the compiler service
import uuid
from services.ATS import calculate_matching_score
from io import BytesIO

router = APIRouter()

@router.post("/enhance")
async def enhance_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    template_name: Optional[str] = Form(None),  # Make template_name optional
    additional_info: str = Form(...)
):
    try:
        # Parse the resume and job description
        parsed_resume = await parse_resume(file)
        parsed_job_description = await parse_job_description(job_description)

        # Load template mapping from tex.json
        try:
            with open("templates/tex.json", "r") as f:
                templates = json.load(f)["templates"]
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to load templates: {str(e)}"
            )

        # Find matching template file or use default
        if template_name:
            template_file = next(
                (t["fileName"] for t in templates if t["name"] == template_name),
                templates[0]["fileName"]  # Default to first template if no match found
            )
        else:
            template_file = templates[0]["fileName"]  # Default to first template if no template_name provided

        # Generate enhanced resume with LaTeX
        result = await generate_enhanced_resume(
            parsed_resume=parsed_resume,
            job_description=parsed_job_description,
            template_file=template_file,
            additional_info=additional_info
        )

        # Compile LaTeX to PDF in memory
        try:
            pdf_bytes = await compile_latex_to_pdf(result["latex_code"])
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF compilation failed: {str(e)}"
            )

        # Create a BytesIO stream from the PDF bytes
        pdf_stream = BytesIO(pdf_bytes)

        # Return the generated PDF as a streaming response
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=enhanced_resume.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ats")
async def ats_analysis(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    print("In the ATS route")
    try:
        # Parse the current resume
        candidate_profile = await parse_resume(file)

        # Parse the job description
        job_requirements = await parse_job_description(job_description)

        # Calculate matching score
        matching_score = await calculate_matching_score(
            job_requirements=job_requirements,
            candidate_profile=candidate_profile
        )

        return matching_score

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))