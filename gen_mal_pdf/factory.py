from pathlib import Path
import json
import datetime
import random
import string
import re
from gen_skelton import load_squelette

OUTPUT_DIR = Path("suspicious_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Charger les payloads (comme avant)
try:
    with open("payloads.json", encoding="utf-8") as f:
        PAYLOADS = json.load(f)
except FileNotFoundError:
    print("payloads.json introuvable → payloads par défaut")
    PAYLOADS = {
        "js_classic": {"simple_alert": 'app.alert("Test simple");'},
        "js_cve": {"uaf_basic": 'var a=[];for(var i=0;i<1000;i++){a[i]=new ArrayBuffer(0x100);}app.alert("UaF sim");'},
        "non_js": {
            "ttf_oob": "/FontFile2 << /Length 88 /Filter /FlateDecode >> stream\n(fake TTF bad header) endstream",
            "jbig2_heap": "/Filter /JBIG2Decode /DecodeParms << /JBIG2Globals 10 0 R >> stream\n(bad JBIG2 segment) endstream"
        },
        "openaction_sim": {
            "simple": 'app.alert("OpenAction déclenché !");',
            "launch": 'app.launchURL("https://example.invalid", true);',
            "obf": 'eval(unescape("%u0061%u0070%u0070%u002e%u0061%u006c%u0065%u0072%u0074%u0028%u0022%u4f%u7065%u6e41%u6374%u696f%u6e%u0022%u0029%u003b"));'
        }
    }

SQUELETTE_PATH = Path("squelette.txt")  # Copie le squelette ci-dessus dans ce fichier

VARIANTS = [
    # Exemples avec /OpenAction réel
    ("openaction_sim", "simple",   "oa_simple",    "OpenAction → alert simple", True),
    ("openaction_sim", "launch",   "oa_launch",    "OpenAction → launch URL", True),
    ("openaction_sim", "obf",      "oa_obf",       "OpenAction → JS obf unescape", True),

    # JS indirect via /Names
    ("js_classic", "simple_alert", "names_simple", "JS via /Names dictionary", True),

    # Parsing heavy (non-JS) injectés dans resources ou xobject
    ("non_js", "ttf_oob",    "parse_ttf",   "Malformed TTF dans font resource", False),
    ("non_js", "jbig2_heap", "parse_jbig2", "JBIG2 stream suspect", False),

    # Combo OpenAction + autre chose
    ("openaction_sim", "simple",   "oa_ttf_combo", "OpenAction + TTF suspect", True),
]

def escape_js_for_pdf(js_code):
    """Échappe ( ) \ pour /JS (string littérale PDF)"""
    return js_code.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def random_garbage_stream(length=80):
    garbage = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"(garbage-{garbage})"


def inject_payload(squelette, cat, key, variant_name, use_js):
    content = squelette

    payload = PAYLOADS.get(cat, {}).get(key, "")
    if not payload:
        return content

    escaped = escape_js_for_pdf(payload)

    if "openaction_sim" in cat or "oa_" in variant_name:
        # Remplacer le /JS de l'OpenAction
        content = re.sub(
            r'/JS \([^)]*\)',
            f'/JS ({escaped})',
            content,
            count=1
        )
        print(f"  → /OpenAction modifié avec payload {key}")

    elif "names" in variant_name:
        # Remplacer le JS indirect dans /Names
        content = re.sub(
            r'/JS \([^)]*\)',
            f'/JS ({escaped})',
            content,
            count=1  # le deuxième /JS (objet 6)
        )
        print(f"  → /Names → JS indirect modifié")

    elif "parse_" in variant_name and "non_js" in cat:
        # Injecter dans le stream de contenu (obj 7) ou resources
        if "ttf" in key:
            # Ajout dans /Resources /Font
            injection = f"/FontDescriptor << /FontFile2 << /Length 80 >> stream\n{payload}\nendstream >>"
            content = content.replace(
                "/BaseFont /Helvetica >>",
                f"/BaseFont /Helvetica {injection} >>"
            )
        elif "jbig2" in key:
            # Ajout d'un /XObject dans /Resources
            xobj = f"/XObject << /Im1 << /Subtype /Image /Filter {payload} >> >>"
            content = content.replace(
                "/Font << /F1 8 0 R >>",
                f"/Font << /F1 8 0 R >> {xobj}"
            )
        print(f"  → Payload parsing injecté dans content/resources")

    return content

def generate_pdf(variant):
    cat, key, name, desc, use_js = variant

    squelette = load_squelette()
    modified = inject_payload(squelette, cat, key, name, use_js)

    # Ajout léger de random pour éviter signatures identiques
    modified += f"\n% Random marker: {random_garbage_stream(40)}"

    #timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"susp_{name}.pdf"

    with open(filename, "wb") as f:
        f.write(modified.encode("latin-1", errors="strict"))

    print(f"→ {filename.name:50} | {desc}")

def main():
    print(f"Génération de {len(VARIANTS)} PDF via squelette modifiable ...\n")
    for v in VARIANTS:
        generate_pdf(v)
    print(f"\nPDF créés dans : {OUTPUT_DIR.resolve()}")
    print("Vérifie avec pdfid.py ou peepdf → cherche /OpenAction, /JavaScript, /JBIG2Decode, etc.")

if __name__ == "__main__":
    main()