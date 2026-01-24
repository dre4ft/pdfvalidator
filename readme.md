# PDF Validator Pipeline

Pipeline Python de validation et de durcissement de fichiers PDF basée sur **YARA**, la **conversion PDF/A** et une logique récursive de traitement sécurisé.

Ce projet a pour objectif de :

* détecter des PDFs **malveillants ou suspects** à l’aide de règles YARA,
* neutraliser les contenus actifs en convertissant les fichiers en **PDF/A**,
* éviter les boucles infinies de conversion,
* supprimer de manière contrôlée les fichiers jugés dangereux,
* conserver une **traçabilité complète** via des logs.

---

## 🧠 Principe général

Le pipeline applique la logique suivante :

1. Analyse du PDF avec YARA
2. Classification : `bénin`, `suspect`, `malveillant`
3. Actions associées :

| Verdict     | Action                                            |
| ----------- | ------------------------------------------------- |
| bénin       | Conversion en PDF/A + suppression du PDF original |
| suspect     | Conversion en PDF/A + **réanalyse récursive**     |
| malveillant | Suppression sécurisée immédiate                   |

Un mécanisme de protection empêche qu’un fichier soit converti **plusieurs fois en PDF/A** (détection via le nom `_pdfa`).

---

## 📁 Structure du projet (attendue)

```
.
├── pdf_validator.py        # main (ce fichier)
├── yara_detection.py       # chargement et scan YARA
├── ghostscript.py          # conversion PDF → PDF/A
├── shredder.py             # suppression sécurisée
├── rules/
│   └── pdf_yara_rules.yar
├── suspect_files/          # PDFs bloqués par protection anti-boucle
├── pipeline.log            # journal d’exécution
```

---

## ▶️ Utilisation

### Analyse d’un fichier unique

```bash
python pdf_validator.py document.pdf
```

### Analyse d’un répertoire

```bash
python pdf_validator.py ./pdfs/
```

Tous les fichiers `.pdf` du dossier seront traités.

---

## ⚙️ Détail du fonctionnement

### `pipeline(pdf_path: str)`

Fonction principale de traitement.

Étapes :

* vérifie l’existence du fichier
* charge les règles YARA (`load_yara_rules()`)
* lance l’analyse (`simple_scan()`)
* applique la logique de décision
* écrit un log horodaté dans `pipeline.log`

Protection anti-boucle :

```text
si le nom contient plus de 2 fois '_pdfa' → arrêt + déplacement dans suspect_files/
```

---

### `runner(path: str)`

* Si `path` est un fichier → traitement direct
* Si `path` est un dossier → traitement de tous les `.pdf`
* Sinon → erreur

---

### `main()`

Point d’entrée CLI.

```text
Usage: python pdf_validator.py <path_to_pdf_or_directory>
```

---

## 🧪 Dépendances

* Python ≥ 3.9
* YARA
* Ghostscript

Modules Python internes :

* `yara_detection`
* `ghostscript`
* `shredder`

⚠️ Ces modules doivent être présents et fonctionnels.

---

## 🛡️ Sécurité

* Les fichiers malveillants sont **supprimés**, pas déplacés
* Les fichiers suspects sont **neutralisés** par PDF/A
* Les boucles infinies sont bloquées
* Aucun PDF actif n’est conservé

---

## 📝 Logs

Chaque action est tracée dans `pipeline.log` :

```
YYYY-MM-DD HH:MM:SS - fichier.pdf : [verdict + action]
```

---

## 🚧 Limitations connues

* La détection dépend entièrement de la qualité des règles YARA
* Les PDFs chiffrés ou corrompus peuvent échouer à la conversion
* Ghostscript doit être installé côté système

---
