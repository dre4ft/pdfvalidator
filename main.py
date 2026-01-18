import os 
from runner import iter, run_validation
from kpi import gen_kpi, save_kpi, mal_kpi, ben_kpi
from caster import add_fake_pdfa_metadata

if not os.path.isdir("results"):
    os.mkdir("results")

def main(): 
    

    #iter("benign")
    iter("suspicious_pdfs")

    gen_kpi("results")
    save_kpi(mal_kpi, "malicious_kpi.json")
    #save_kpi(ben_kpi, "benign_kpi.json")

if __name__ == "__main__":
    #main()
    path = "suspicious_pdfs/susp_20260118_130053_classic_obf2.pdf"
    add_fake_pdfa_metadata(path, "fake_pdfa_"+os.path.basename(path))
    run_validation(True, "fake_pdfa_susp_20260118_130053_classic_obf2.pdf")
    