#!/usr/bin/env python3
"""
Generate PDF from BnF Ms. Fr. 640 XML manuscript data.
This script converts the translation XML to a formatted PDF.
"""

import xml.etree.ElementTree as ET
import sys
from pathlib import Path

def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))

def process_element(elem, depth=0):
    """
    Recursively process XML elements and convert to HTML.
    Returns HTML string.
    """
    tag = elem.tag
    text = elem.text or ""
    tail = elem.tail or ""

    # Handle different element types
    html = ""

    # Root element
    if tag == "all":
        html = '<div class="manuscript">\n'
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</div>\n'
        return html

    # Structural elements
    elif tag == "div":
        div_id = elem.get("id", "")
        categories = elem.get("categories", "")
        html = f'<div class="entry" id="{escape_html(div_id)}" data-categories="{escape_html(categories)}">\n'
        if text.strip():
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</div>\n'
        if tail.strip():
            html += escape_html(tail)
        return html

    elif tag == "head":
        margin = elem.get("margin", "")
        html = f'<h2 class="head {escape_html(margin)}">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</h2>\n'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "ab":
        margin = elem.get("margin", "")
        render = elem.get("render", "")
        classes = f"ab {escape_html(margin)} {escape_html(render)}".strip()
        html = f'<p class="{classes}">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</p>\n'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "hr":
        return '<hr/>\n' + escape_html(tail)

    elif tag == "lb":
        return '<br/>\n' + escape_html(tail)

    # Semantic elements - styled spans
    elif tag == "pn":  # Personal name
        html = '<span class="pn">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "pl":  # Place
        html = '<span class="pl">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "pro":  # Profession
        html = '<span class="pro">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "m":  # Material
        html = '<span class="m">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "pa":  # Plant
        html = '<span class="pa">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "al":  # Animal
        html = '<span class="al">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "tl":  # Tool
        html = '<span class="tl">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "ms":  # Measurement
        html = '<span class="ms">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "env":  # Environment
        html = '<span class="env">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "tmp":  # Temporal
        html = '<span class="tmp">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "bp":  # Body part
        html = '<span class="bp">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "cn":  # Currency
        html = '<span class="cn">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "mu":  # Musical instrument
        html = '<span class="mu">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "md":  # Medical
        html = '<span class="md">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "wp":  # Weapon
        html = '<span class="wp">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "sn":  # Sense
        html = '<span class="sn">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "df":  # Definition
        html = '<span class="df">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # Language elements
    elif tag == "la":  # Latin
        html = '<span class="la">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "fr":  # French
        html = '<span class="fr">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "it":  # Italian
        html = '<span class="it">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "de":  # German
        html = '<span class="de">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "el":  # Greek
        html = '<span class="el">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "oc":  # Occitane
        html = '<span class="oc">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "po":  # Poitevin
        html = '<span class="po">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # Transcription elements
    elif tag == "emph":  # Emphasized
        html = '<em>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</em>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "underline":  # Underlined
        html = '<u>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</u>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "superscript" or tag == "sup":  # Superscript/Supplied
        html = '<sup>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</sup>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "del":  # Deletion
        html = '<del>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</del>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "add":  # Addition
        html = '<ins>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</ins>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "exp":  # Expansion
        html = '<span class="exp">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "corr":  # Correction
        html = '<span class="corr">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "ill":  # Illegible
        html = '<span class="ill">[illegible]'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "gap":  # Gap
        return '<span class="gap">[gap]</span>' + escape_html(tail)

    elif tag == "mark":  # Mark/Symbol
        html = '<span class="mark">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    elif tag == "comment":  # Comment reference
        rid = elem.get("rid", "")
        return f'<sup class="comment-ref">[{escape_html(rid)}]</sup>' + escape_html(tail)

    elif tag == "figure":  # Figure
        fig_id = elem.get("id", "")
        alt_text = elem.get("alt-text", "")
        html = f'<div class="figure" id="{escape_html(fig_id)}">'
        html += f'<p class="figure-placeholder">[Figure: {escape_html(alt_text) if alt_text else fig_id}]</p>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</div>\n'
        if tail:
            html += escape_html(tail)
        return html

    # Default: just process children and text
    else:
        html = ""
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        if tail:
            html += escape_html(tail)
        return html

def get_css():
    """Return CSS stylesheet for the PDF."""
    return """
    @page {
        size: letter;
        margin: 1in;
    }

    body {
        font-family: "Garamond", "Georgia", "Times New Roman", serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #000;
    }

    .manuscript {
        max-width: 100%;
    }

    /* Entry structure */
    .entry {
        margin-bottom: 2em;
        page-break-inside: avoid;
    }

    .head {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        color: #2c3e50;
        border-bottom: 1px solid #ccc;
        padding-bottom: 0.25em;
    }

    .ab {
        margin-bottom: 1em;
        text-align: justify;
    }

    /* Semantic elements - different colors for different categories */
    .pn {
        font-weight: 600;
        color: #16a085;
    }

    .pl {
        font-weight: 500;
        color: #2980b9;
    }

    .pro {
        font-variant: small-caps;
        color: #8e44ad;
    }

    .m {
        color: #d35400;
    }

    .pa {
        color: #27ae60;
    }

    .al {
        color: #c0392b;
    }

    .tl {
        color: #7f8c8d;
    }

    .ms {
        font-family: monospace;
        font-size: 0.95em;
    }

    .env {
        color: #16a085;
    }

    .tmp {
        font-style: italic;
        color: #95a5a6;
    }

    .bp {
        color: #e74c3c;
    }

    .cn {
        color: #f39c12;
    }

    .mu {
        color: #9b59b6;
    }

    .md {
        color: #e67e22;
    }

    .wp {
        color: #c0392b;
    }

    .sn {
        font-style: italic;
    }

    .df {
        font-weight: 500;
    }

    /* Language elements */
    .la, .fr, .it, .de, .el, .oc, .po {
        font-style: italic;
    }

    .la {
        color: #34495e;
    }

    /* Transcription elements */
    em {
        font-style: italic;
    }

    u {
        text-decoration: underline;
    }

    sup {
        vertical-align: super;
        font-size: 0.8em;
    }

    del {
        text-decoration: line-through;
        color: #95a5a6;
    }

    ins {
        text-decoration: none;
        border-bottom: 1px dotted #999;
    }

    .exp {
        font-style: normal;
    }

    .corr {
        color: #3498db;
    }

    .ill {
        color: #95a5a6;
        font-style: italic;
    }

    .gap {
        color: #95a5a6;
        font-style: italic;
    }

    .mark {
        font-weight: bold;
        color: #e74c3c;
    }

    .comment-ref {
        color: #3498db;
        font-size: 0.7em;
    }

    /* Figure placeholder */
    .figure {
        margin: 1em 0;
        padding: 1em;
        background-color: #ecf0f1;
        border-left: 3px solid #3498db;
    }

    .figure-placeholder {
        font-style: italic;
        color: #7f8c8d;
        margin: 0;
    }

    /* Horizontal rule */
    hr {
        border: none;
        border-top: 1px solid #bdc3c7;
        margin: 1em 0;
    }
    """

def xml_to_html(xml_file, output_html):
    """Convert XML file to HTML."""
    print(f"Parsing XML file: {xml_file}")

    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Convert to HTML
    print("Converting XML to HTML...")
    body_html = process_element(root)

    # Create complete HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BnF Ms. Fr. 640 - Translation</title>
    <style>
    {get_css()}
    </style>
</head>
<body>
    <h1>Secrets of Craft and Nature in Renaissance France</h1>
    <h2>BnF Ms. Fr. 640 - English Translation</h2>
    {body_html}
</body>
</html>
"""

    # Write HTML file
    print(f"Writing HTML to: {output_html}")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print("HTML conversion complete!")

def html_to_pdf(html_file, output_pdf):
    """Convert HTML file to PDF using weasyprint."""
    try:
        from weasyprint import HTML
        print(f"Generating PDF from HTML: {html_file}")
        HTML(filename=html_file).write_pdf(output_pdf)
        print(f"PDF generated successfully: {output_pdf}")
        return True
    except ImportError:
        print("\nERROR: weasyprint is not installed.")
        print("Please install it using:")
        print("  pip install weasyprint")
        print("\nNote: weasyprint requires additional system dependencies.")
        print("On macOS, install with: brew install python cairo pango gdk-pixbuf libffi")
        print("On Ubuntu/Debian: apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0")
        return False
    except Exception as e:
        print(f"\nERROR generating PDF: {e}")
        return False

def main():
    """Main function."""
    # Input and output paths
    xml_file = Path("allFolios/xml/tl/all_tl.xml")
    html_file = Path("allFolios/xml/tl/all_tl.html")
    pdf_file = Path("allFolios/xml/tl/all_tl.pdf")

    # Check if XML file exists
    if not xml_file.exists():
        print(f"ERROR: XML file not found: {xml_file}")
        sys.exit(1)

    # Convert XML to HTML
    xml_to_html(xml_file, html_file)

    # Convert HTML to PDF
    success = html_to_pdf(html_file, pdf_file)

    if success:
        print(f"\n✓ PDF generation complete!")
        print(f"  Output: {pdf_file}")
    else:
        print(f"\n✓ HTML generation complete!")
        print(f"  Output: {html_file}")
        print(f"\nYou can open the HTML file in a browser and print to PDF manually,")
        print(f"or install weasyprint to generate PDFs automatically.")

if __name__ == "__main__":
    main()
