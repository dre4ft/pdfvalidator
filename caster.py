from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    TextStringObject,
    StreamObject,
)
from datetime import datetime
import uuid


def add_fake_pdfa_metadata(
    input_pdf_path: str,
    output_pdf_path: str,
    pdfa_level: str = "1b",
):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Copie des pages
    for page in reader.pages:
        writer.add_page(page)

    # Copie des métadonnées existantes
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # Métadonnées classiques PDF
    now = datetime.utcnow()
    utc_offset = "-00'00'"
    date_str = now.strftime(f"D:%Y%m%d%H%M%S{utc_offset}")

    writer.add_metadata({
        "/Title": "Document test PDF/A",
        "/Author": "Test",
        "/Subject": "Simulation PDF/A",
        "/Keywords": "PDF/A test",
        "/Creator": "pypdf fake PDF/A",
        "/Producer": "Fake PDF/A Generator",
        "/CreationDate": date_str,
        "/ModDate": date_str,
    })

    # Détermination PDF/A
    part = "1" if pdfa_level.startswith("1") else "2" if pdfa_level.startswith("2") else "3"
    conformance = "B"
    amd = "2005" if part == "1" else "2011" if part == "2" else "2020"

    doc_id = f"uuid:{uuid.uuid4()}"
    now_iso = now.isoformat() + "Z"

    # XMP XML (PDF/A minimal)
    xmp_xml = f"""<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.4.0">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
    xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"
    pdfaid:part="{part}"
    pdfaid:conformance="{conformance}"
    pdfaid:amd="{amd}"
    xmp:CreateDate="{now_iso}"
    xmp:ModifyDate="{now_iso}"
    xmp:MetadataDate="{now_iso}"
    xmpMM:DocumentID="{doc_id}"
    xmpMM:InstanceID="{doc_id}">
   <pdfaid:Schema>PDF/A schema</pdfaid:Schema>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>""".encode("utf-8")

    # Création du stream Metadata (CORRECT)
    metadata_stream = StreamObject()
    metadata_stream._data = xmp_xml
    metadata_stream.update({
        NameObject("/Type"): NameObject("/Metadata"),
        NameObject("/Subtype"): NameObject("/XML"),
    })

    metadata_ref = writer._add_object(metadata_stream)

    # Liaison au catalog
    catalog = writer._root_object
    catalog.update({
        NameObject("/Metadata"): metadata_ref
    })

    # Sauvegarde
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"PDF casté avec XMP ajouté → {output_pdf_path}")
    print(f"Test veraPDF : verapdf --flavour pdfa-{pdfa_level} {output_pdf_path}")
