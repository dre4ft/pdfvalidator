import subprocess
import json
import os
from test.clean_result import clean_result
import time

def run_validation(is_malicious,pdf_path):
    change_ext = False

    if not pdf_path.endswith(".pdf") :
        change_ext = True
        os.rename(pdf_path, pdf_path + ".pdf")
        pdf_path = pdf_path + ".pdf"
    
    process = subprocess.run(
        ["verapdf", "--format", "json", "--flavour","1a",pdf_path],
        stdout=subprocess.PIPE,  
        stderr=subprocess.PIPE,   
        text=True                
    )

    if change_ext:
        og_filename = pdf_path[:-4]  
        os.rename(pdf_path, og_filename)
    
    if process.stderr:
        print("Erreur verapdf:", process.stderr)
    result = clean_result(json.loads(process.stdout))
    #result = process.stdout
    with open(os.path.join("results", os.path.basename(pdf_path) + "_malicious_result.json" if is_malicious else os.path.basename(pdf_path)+"_benign_result.json"), "w") as f:
        json.dump(result, f, indent=4)
    



def iter(dir): 
    is_malicious = False

    if dir != "benign":
        is_malicious = True
        
    for filename in os.listdir(dir):

        run_validation(is_malicious,os.path.join(dir, filename))


if __name__ == "__main__":
   
    iter("benign")