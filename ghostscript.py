import subprocess
import time
import os

def convert_to_pdfa(input_file: str, output_file: str) -> None:
    """Convert PDF to PDF/A-2 format using Ghostscript."""
    cmd = [
        "gs",
        "-dPDFA=2",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-dPDFACompatibilityPolicy=1",
        "-sColorConversionStrategy=RGB",
        "-dEmbedAllFonts=true",
        "-dSubsetFonts=true",
        "-dHaveTransparency=false",
        f"-sOutputFile={output_file}",
        input_file
    ]
    subprocess.run(cmd,stdout=subprocess.PIPE,  
        stderr=subprocess.PIPE,   
        text=True)

