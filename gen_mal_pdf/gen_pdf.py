from fpdf import FPDF
from pathlib import Path
import json
import datetime
import random
import string
import io

# Pour post-traitement pypdf
from pypdf import PdfWriter, PdfReader

OUTPUT_DIR = Path("suspicious_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Charger les payloads depuis JSON (comme avant)
try:
    with open("gen_mal_pdf/payloads.json", encoding="utf-8") as f:
        PAYLOADS = json.load(f)
except FileNotFoundError:
    print("payloads.json non trouvé → utilisation de payloads par défaut")
    PAYLOADS = {
        "js_classic": {
            "simple_alert": 'app.alert("Test simple JS");',
            "obf2_hex": 'var s="6170702e616c65727428224f6266..."); eval(r);',  # tronqué pour exemple
            "uri_submit": 'this.submitForm({cURL:"https://example.invalid",cSubmitAs:"HTML"});'
        },
        "js_cve": {
            "uaf_basic": 'var arr=[];for(var i=0;i<1000;i++){arr[i]=new ArrayBuffer(0x100);}delete arr[500];app.alert("UaF sim");',
            # ... ajoute les autres
        },
        # Ajoute tes autres catégories non_js si besoin (mais pour non-JS, on les affiche en texte)
    }

VARIANTS = [
    # On garde les variantes JS-heavy car pypdf excelle pour ajouter du JS + OpenAction
    ("js_classic", "simple_alert", "classic_simple", "JS alert basique + OpenAction", True, True),
    ("js_classic", "obf2_hex",     "classic_obf2",   "Obfuscation hex + OpenAction", True, True),
    ("js_classic", "uri_submit",   "classic_submit", "submitForm URI + OpenAction", True, True),

    ("js_cve", "uaf_basic",       "cve_uaf",        "UaF spray + OpenAction", True, True),
    ("js_cve", "resetform_corrupt","cve_resetform",  "resetForm corruption + OpenAction", True, True),
    ("js_cve", "font_spray",      "cve_font_spray", "Font spray OOB + OpenAction", True, True),

    # Pour non-JS : on génère avec fpdf (texte visible) sans JS ajouté par pypdf
    ("non_js", "ttf_oob",         "parse_ttf_oob",   "Malformed TTF font sim (no JS)", False, False),
    ("non_js", "jbig2_heap",      "parse_jbig2",     "JBIG2 malformed (no JS)", False, False),
    # ... ajoute les autres non-JS si tu veux
]

def random_garbage_stream():
    garbage = "".join(random.choices(string.ascii_letters + string.digits + " .,;:!?", k=140))
    return f"(garbage stream - {garbage[:60]}...)"

def generate_base_pdf(variant):
    """
    Génère le PDF de base avec fpdf2 (contenu visible + simulation non-JS)
    Retourne un BytesIO prêt à être lu par pypdf
    """
    cat, payload_key, name, desc, is_js, add_openaction = variant

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 12, f"SUSPECT PDF - {name.upper()}", ln=1, align="C")
    pdf.ln(8)
    pdf.multi_cell(0, 8, f"{desc}\n\nCe PDF est INOFFENSIF mais simule des marqueurs suspects.\n"
                         f"Payload catégorie : {cat} / clé : {payload_key}")

    payload_content = PAYLOADS.get(cat, {}).get(payload_key, "")

    if is_js and payload_content:
        # On ne peut pas ajouter le JS ici → on le fait après avec pypdf
        pdf.write(text=f"[JS simulé : {payload_content[:80]}...]\n(sera ajouté via pypdf)\n\n")
        
        pdf.ln(10)
        pdf.set_text_color(0, 0, 180)
        pdf.write(10, "[Cliquer pour simuler]", link=pdf.add_link())  # lien vide, juste visuel

    else:
        # Non-JS : affiche le pseudo-code comme texte
        pdf.ln(10)
        pdf.set_font("Courier", size=9)
        pdf.multi_cell(0, 5, payload_content or "[Aucun payload textuel]")

    if "multi_filter" in name or "garbage" in name:
        pdf.multi_cell(0, 6, "Simulation multi /Filter : [/FlateDecode /ASCII85Decode /JBIG2Decode ...]")
        pdf.multi_cell(0, 6, random_garbage_stream())

    # Sauvegarde temporaire en mémoire
    output_stream = io.BytesIO()
    pdf.output(output_stream)
    output_stream.seek(0)
    return output_stream

def add_js_with_pypdf(input_stream: io.BytesIO, js_code: str, output_path: Path):
    """
    Post-traite avec pypdf pour ajouter le JS + OpenAction
    """
    reader = PdfReader(input_stream)
    writer = PdfWriter()

    # Copie toutes les pages
    for page in reader.pages:
        writer.add_page(page)

    if js_code:
        # Ajoute le JS qui s'exécute à l'ouverture (/OpenAction)
        writer.add_js(js_code)
        print(f"  → JS ajouté via pypdf.add_js() → /OpenAction créé automatiquement")

    # Écrit le fichier final
    with open(output_path, "wb") as f:
        writer.write(f)

def create_suspicious_pdf(variant):
    cat, payload_key, name, desc, is_js, add_openaction = variant

    # 1. Génère base avec fpdf
    base_stream = generate_base_pdf(variant)

    payload_content = PAYLOADS.get(cat, {}).get(payload_key, "")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"susp_{timestamp}_{name}.pdf"

    if is_js and payload_content and add_openaction:
        # 2. Ajoute JS + OpenAction avec pypdf
        add_js_with_pypdf(base_stream, payload_content, filename)
    else:
        # Pour non-JS ou sans JS : copie simplement le stream fpdf
        base_stream.seek(0)
        with open(filename, "wb") as f:
            f.write(base_stream.read())

    print(f"→ {filename.name:50} | {desc[:60]}")

def main():
    print(f"Génération de {len(VARIANTS)} variantes (fpdf → pypdf post-process)...\n")
    for variant in VARIANTS:
        create_suspicious_pdf(variant)
    print(f"\nFichiers créés dans : {OUTPUT_DIR.resolve()}")
    print("Vérifie avec pdfid / peepdf / veraPDF → cherche /OpenAction et /JavaScript")

if __name__ == "__main__":
    main()
