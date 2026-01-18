from pathlib import Path


SQUELETTE_PATH = Path("squelette.txt") 

def load_squelette():
    if not SQUELETTE_PATH.exists():
        print("Création squelette.txt automatique")
        with open(SQUELETTE_PATH, "w", encoding="latin-1") as f:
            f.write("""%PDF-1.7
1 0 obj
<< /Type /Catalog
   /Pages 2 0 R
   /OpenAction 3 0 R
   /Names << /JavaScript 4 0 R >>
>>
endobj
2 0 obj << /Type /Pages /Kids [5 0 R] /Count 1 >> endobj
3 0 obj << /S /JavaScript /JS (app.alert\\("DEFAULT OPENACTION - harmless"\\);) >> endobj
4 0 obj << /Names [(alert) 6 0 R] >> endobj
5 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 7 0 R /Resources << /Font << /F1 8 0 R >> >> /Annots [9 0 R] >> endobj
6 0 obj << /S /JavaScript /JS (app.alert\\("JS indirect - harmless"\\);) >> endobj
7 0 obj << /Length 120 >> stream
BT /F1 14 Tf 100 700 Td (Document test - inoffensif) Tj ET
endstream endobj
8 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
9 0 obj << /Type /Annot /Subtype /Link /Rect [100 600 300 650] /A << /S /URI /URI (https://example.invalid) >> >> endobj
xref
0 10
0000000000 65535 f
0000000010 00000 n
0000000080 00000 n
0000000160 00000 n
0000000240 00000 n
0000000320 00000 n
0000000450 00000 n
0000000530 00000 n
0000000650 00000 n
0000000740 00000 n
trailer << /Size 10 /Root 1 0 R >>
startxref
820
%%EOF""")
    with open(SQUELETTE_PATH,"r", encoding="latin-1",newline="\n") as f:
        return f.read()