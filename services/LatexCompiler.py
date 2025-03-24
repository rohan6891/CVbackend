import subprocess
import os
import tempfile
from pathlib import Path

class LatexCompilationError(Exception):
    pass

async def compile_latex_to_pdf(latex_code: str, output_filename: str) -> str:
    """
    Compiles LaTeX code to PDF and returns the path to the generated PDF file.
    """
    # Create output directory if it doesn't exist
    output_dir = Path("generated_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file = os.path.join(tmpdirname, 'resume.tex')
        with open(tex_file, 'w') as f:
            f.write(latex_code)
        
        # Run pdflatex command
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', tmpdirname, tex_file],
            capture_output=True,
            text=True
        )
        
        pdf_file = os.path.join(tmpdirname, 'resume.pdf')
        if os.path.exists(pdf_file):
            output_path = output_dir / output_filename
            os.replace(pdf_file, output_path)
            return str(output_path)
        else:
            error_msg = f"Compilation error: {result.stdout}\n{result.stderr}"
            raise LatexCompilationError(error_msg)