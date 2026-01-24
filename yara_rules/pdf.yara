/*
This Yara ruleset is under the GNU-GPLv2 license ([http://www.gnu.org/licenses/gpl-2.0.html](http://www.gnu.org/licenses/gpl-2.0.html))
*/
// -----------------------------------------------------------------------------
// Rule set: PDF Malicious Heuristics & Exploit Indicators (2020–2025)
// Weights adjusted for:
//   SUSPICIOUS_THRESHOLD = 40
//   MALICIOUS_THRESHOLD  = 70
// -----------------------------------------------------------------------------

rule pdf_malicious_structural
{
meta:
description = "Detect suspicious structural PDF elements that often appear in exploits"
weight = 30
strings:
$pdf_magic = "%PDF-"
$openaction = "/OpenAction"
$additional_action = "/AA"
$acroform = "/AcroForm"
$xfa = "/XFA"
condition:
$pdf_magic and any of ($openaction, $additional_action, $acroform, $xfa)
}

rule pdf_js_action_exploit
{
meta:
description = "Detect JavaScript actions within PDF that could be exploited"
weight = 55
strings:
$js_s_action = "/S /JavaScript"
$js_inside = "JavaScript("
$xfa_inline = "/XFA"
$js_event1 = "this.exportXFAData" nocase ascii
$js_event2 = "app.openDoc" nocase ascii
$js_alert  = "app.alert" nocase ascii
condition:
uint16(0) == 0x2550 and any of ($js_s_action, $js_inside) and any of ($xfa_inline, $js_event1, $js_event2, $js_alert)
}

rule pdf_submitform_network
{
meta:
description = "Detect /SubmitForm with URL destination"
weight = 45
strings:
$submit_form = "/S /SubmitForm"
$fs_url = "/FS /URL"
$uri_http = /https?:/// nocase
condition:
all of ($submit_form, $fs_url, $uri_http)
}

rule pdf_uri_action
{
meta:
description = "Detect PDF Actions pointing to remote URI"
weight = 30
strings:
$uri_action = "/A"
$uri_http = /https?:/// nocase
condition:
$uri_action and $uri_http
}

rule pdf_embedded_stream_suspect
{
meta:
description = "Detect embedded streams that may contain obfuscated code"
weight = 25
strings:
$stream = "stream" nocase
$hex_obf = /\\x[0-9A-Fa-f]{2}/
$asciihex = "/ASCIIHexDecode"
$ascii85 = "/ASCII85Decode"
condition:
$stream and any of ($hex_obf, $asciihex, $ascii85)
}

rule pdf_meta_suspicious
{
meta:
description = "Detect suspicious PDF metadata fields"
weight = 10
strings:
$author = "/Author" nocase
$creator = "/Creator" nocase
$producer = "/Producer" nocase
$title = "/Title" nocase
condition:
any of ($author, $creator, $producer, $title)
}

rule pdf_openaction_present : PDF
{
meta:
weight = 25
strings:
$oa = "/OpenAction"
condition:
$oa
}

rule pdf_openaction_network : PDF
{
meta:
weight = 60
strings:
$oa = "/OpenAction"
$url = "/FS /URL"
$http = /https?:///
condition:
all of ($oa, $url) and $http
}

rule pdf_submitform : PDF
{
meta:
weight = 30
strings:
$sf = "/S /SubmitForm"
condition:
$sf
}

rule pdf_js_action : PDF
{
meta:
weight = 30
strings:
$js = "/S /JavaScript"
condition:
$js
}

rule PDF_Embedded_Exe : PDF
{
meta:
ref = "[https://github.com/jacobsoo/Yara-Rules/blob/master/PDF_Embedded_Exe.yar](https://github.com/jacobsoo/Yara-Rules/blob/master/PDF_Embedded_Exe.yar)"
weight = 70
strings:
$header = {25 50 44 46}
$Launch_Action = {3C 3C 2F 53 2F 4C 61 75 6E 63 68 2F 54 79 70 65 2F 41 63 74 69 6F 6E 2F 57 69 6E 3C 3C 2F 46}
$exe = {3C 3C 2F 45 6D 62 65 64 64 65 64 46 69 6C 65 73}
condition:
$header at 0 and $Launch_Action and $exe
}

// -----------------------------------------------------------------------------
// Low-signal / context rules
// -----------------------------------------------------------------------------

rule suspicious_obfuscation : PDF raw
{
meta:
weight = 20
strings:
$magic = { 25 50 44 46 }
$reg = /\/\w#[a-zA-Z0-9]{2}#[a-zA-Z0-9]{2}/
condition:
$magic in (0..1024) and #reg > 5
}

rule header_evasion : PDF raw
{
meta:
weight = 15
strings:
$magic = { 25 50 44 46 }
condition:
$magic in (5..1024) and #magic == 1
}
rule PDF_Malicious_XML_XFA
{
    meta:
        description = "Detects malicious PDF using embedded XML/XFA"
        author = "ChatGPT"
        reference = "Generic PDF XML/XFA malware detection"

    strings:
        $pdf_header = "%PDF"
        $xfa        = "/XFA"
        $xml_tag1   = "<xfa:"
        $xml_tag2   = "<xdp:xdp"
        $js         = "script" nocase
        $launch     = "/Launch"

    condition:
        $pdf_header at 0 and
        $xfa and
        any of ($xml_tag*) and
        any of ($js, $launch)
}
