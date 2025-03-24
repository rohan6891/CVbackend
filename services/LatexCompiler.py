import subprocess
import os
import tempfile
from pathlib import Path
from io import BytesIO

class LatexCompilationError(Exception):
    pass

async def compile_latex_to_pdf(latex_code: str) -> bytes:
    """
    Compiles LaTeX code to PDF and returns the PDF file as bytes.
    """
    # Write LaTeX code to a temporary .tex file
    with open("temp.tex", "w") as f:
        f.write(latex_code)

    # Compile the .tex file to PDF
    subprocess.run(["pdflatex", "temp.tex"], check=True)

    # Read the generated PDF file
    with open("temp.pdf", "rb") as f:
        pdf_bytes = f.read()

    # Clean up temporary files
    os.remove("temp.tex")
    os.remove("temp.pdf")

    return pdf_bytes