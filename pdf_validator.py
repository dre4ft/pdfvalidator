from yara_detection import simple_scan, load_yara_rules
from ghostscript import convert_to_pdfa
import os 
from datetime import datetime 
import sys
from shredder import erase_pipeline



def pipeline(pdf_path: str) :
    if not os.path.exists(pdf_path) :
        raise FileNotFoundError(f"Le fichier {pdf_path} n'existe pas.")
    rules = load_yara_rules()
    verdict = simple_scan(pdf_path,rules)['verdict']
    if pdf_path.count('_pdfa')> 2 : 
        dir = "suspect_files"
        if not os.path.exists(dir) :
            os.makedirs(dir)
        os.rename(pdf_path, os.path.join(dir, os.path.basename(pdf_path)))
        log = "[#] Le fichier a déjà été converti plusieurs fois en PDF/A, arrêt de la pipeline pour éviter une boucle infinie. \n Le fichier est déplacé dans le dossier suspect_files."
    else : 
        if verdict == "malveillant" : 
            log = "[!] Le fichier est malveillant, suppression en cours..."
            erase_pipeline(pdf_path)
        else : 
            pdfa_path = pdf_path.replace('.pdf','_pdfa.pdf')
            convert_to_pdfa(pdf_path, pdfa_path)
            erase_pipeline(pdf_path)
            if verdict == "suspect" :
                log = "[*] Le fichier est suspect, conversion en PDF/A effectuée analyse complémentaire en cours..."
                pipeline(pdfa_path)
            else : 
                log = "[+] Le fichier est bénin, conversion en PDF/A effectuée."
    with open('pipeline.log','a') as f :
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{time} - {pdf_path} : {log}\n")

def runner(path: str) :
    if os.path.isfile(path) :
        pipeline(path)
    elif os.path.isdir(path) :
        for filename in os.listdir(path) :
            if filename.endswith('.pdf') :
                pipeline(os.path.join(path,filename))
    else : 
        raise ValueError(f"{path} n'est ni un fichier ni un répertoire valide.")


def main():
    if len(sys.argv) != 2 :
        print("Usage: python pdf_validator.py <path_to_pdf_or_directory>")
        sys.exit(1)
    input_path = sys.argv[1]
    runner(input_path) 

if __name__ == "__main__":
    main()



