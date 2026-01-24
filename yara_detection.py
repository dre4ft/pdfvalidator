import sys
import argparse
from pathlib import Path
import yara
import json
from typing import List, Dict, Any


DEFAULT_RULE_FILES = [Path("yara_rules/pdf.yara")]
SUSPICIOUS_THRESHOLD = 40
MALICIOUS_THRESHOLD  = 70

def load_yara_rules(rule_paths: List[Path] = None) -> yara.Rules:
    """Compile toutes les règles YARA passées en paramètre"""
    if rule_paths is None:
        rule_paths = DEFAULT_RULE_FILES
    sources = {}
    for path in rule_paths:
        if path.exists():
            sources[path.name] = path.read_text(encoding="utf-8")
        else:
            print(f"[!] Règle non trouvée : {path}")

    if not sources:
        print("[!] Aucune règle valide trouvée.")
        sys.exit(1)

    try:
        rules = yara.compile(sources=sources)
       # print(f"[+] {len(sources)} règles YARA compilées avec succès")
        return rules
    except Exception as e:
        print(f"[!] Erreur de syntaxe dans les règles YARA :\n{e}")
        sys.exit(1)


def scan_pdf_with_yara(pdf_path: Path, rules: yara.Rules) -> Dict[str, Any]:
    """Scanne un fichier PDF avec les règles YARA"""
    try:
        matches = rules.match(str(pdf_path))
    except Exception as e:
        return {
            "file": str(pdf_path),
            "error": str(e),
            "matches": [],
            "score": 0,
            "verdict": "erreur"
        }

    total_score = 0
    detections = []

    for match in matches: 
        rule_name = match.rule
        score = match.meta.get("weight", 10)  
        total_score += score

        detections.append({
            "rule": rule_name,
            "score": score,
            "meta": match.meta,
            "matched_strings": [
                {
                    "name": s.identifier,
                    "matches": [
                        {
                            "offset": inst.offset,
                            "data": inst.matched_data.hex()[:32] + "..."
                        }
                        for inst in s.instances
                    ]
                }
                for s in match.strings
            ]
        })

    verdict = "malveillant" if total_score >= MALICIOUS_THRESHOLD else \
              "suspect" if total_score >= SUSPICIOUS_THRESHOLD else "bénin"

    return {
        "file": str(pdf_path),
        "score": total_score,
        "verdict": verdict,
        "detections": detections,
    }


def main():
    parser = argparse.ArgumentParser(description="Scanner PDF avec des règles YARA personnalisables")
    parser.add_argument("target", help="Fichier PDF ou dossier à scanner")
    parser.add_argument("--rules", nargs="+", help="Fichiers .yar spécifiques (sinon utilise les règles par défaut)")
    parser.add_argument("--json", action="store_true", help="Sortie au format JSON")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"[!] Chemin introuvable : {target}")
        sys.exit(1)

    if args.rules:
        rule_paths = [Path(r) for r in args.rules]
    else:
        rule_paths = DEFAULT_RULE_FILES

    if not rule_paths:
        print("[!] Aucune règle trouvée. Créez un dossier yara_rules/ avec vos .yar")
        sys.exit(1)

    yara_rules = load_yara_rules(rule_paths)

    results = []

    if target.is_file() and target.suffix.lower() == ".pdf":
        result = scan_pdf_with_yara(target, yara_rules)
        results.append(result)
    elif target.is_dir():
        for pdf_file in target.rglob("*.pdf"):
            result = scan_pdf_with_yara(pdf_file, yara_rules)
            results.append(result)
    else:
        print("[!] Spécifiez un fichier .pdf ou un dossier")
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(f"\n{r['file']}:")
            print(f"  Score : {r['score']}")
            print(f"  Verdict : {r['verdict'].upper()}")
            if r['detections']:
                print("  Détections :")
                for d in r['detections']:
                    print(f"    - {d['rule']} (score {d['score']})")
                    if d['meta']:
                        print(f"      Meta: {d['meta']}")

    if len(results) > 1:
        malicious = sum(1 for r in results if r["score"] >= MALICIOUS_THRESHOLD)
        suspicious = sum(1 for r in results if SUSPICIOUS_THRESHOLD <= r["score"] < MALICIOUS_THRESHOLD)
        print(f"\nRésumé : {malicious} malveillants | {suspicious} suspects | {len(results)-malicious-suspicious} bénins")

def simple_scan(pdf_path: str,rules = None) :
    """Fonction utilitaire pour scanner un PDF avec les règles par défaut"""
    yara_rules = load_yara_rules() if rules is None else rules    
    return scan_pdf_with_yara(Path(pdf_path), yara_rules)

if __name__ == "__main__":
   #main()
   print(simple_scan("benign/0_ea-2a_1108.pdf"))