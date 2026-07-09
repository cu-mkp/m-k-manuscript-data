#!/usr/bin/env python3
"""
BnF Ms. Fr. 640 XML to PDF Converter
=====================================

This script converts the Making and Knowing Project's XML manuscript data
(specifically the English translation version) into a formatted PDF document.
"""

import xml.etree.ElementTree as ET
import sys
import csv
import argparse
from pathlib import Path

# ==============================================================================
# HTML UTILITY FUNCTIONS
# ==============================================================================

def escape_html(text):
    """
    Escape HTML special characters to prevent rendering issues.
    """
    if not text:
        return ""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )

# ==============================================================================
# XML TO HTML CONVERSION
# ==============================================================================

def process_element(elem, depth=0, margin_notes=None, endnotes=None, render_semantic=False):
    """
    Recursively process XML elements and convert to styled HTML.
    """
    tag = elem.tag
    text = elem.text or ""
    tail = elem.tail or ""
    html = ""

    if tag == "all":
        html = '<div class="manuscript">\n'
        for child in elem:
            html += process_element(child, depth + 1, endnotes=endnotes, render_semantic=render_semantic)
        html += '</div>\n'
        return html
    elif tag == "div":
        div_id = elem.get("id", "")
        categories = elem.get("categories", "")
        div_margin_notes = []
        html = f'<div class="entry" id="{escape_html(div_id)}" data-categories="{escape_html(categories)}">\n'
        if text.strip():
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=div_margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</div>\n'
        if div_margin_notes:
            html += '<div class="margin-notes">\n'
            html += '<h3 class="margin-notes-header">Margin Notes:</h3>\n'
            for note_html in div_margin_notes:
                html += note_html
            html += '</div>\n'
        if tail.strip():
            html += escape_html(tail)
        return html
    elif tag == "head":
        margin = elem.get("margin", "")
        css_class = "head"
        if "left-middle" in margin or "right-top" in margin:
            css_class += " minor-head"
        html = f'<h3 class="{css_class} {escape_html(margin)}" >'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</h3>\n'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "ab":
        margin = elem.get("margin", "")
        render = elem.get("render", "")
        if margin and margin_notes is not None:
            note_html = f'<div class="margin-note" data-position="{escape_html(margin)}">\n'
            note_html += f'<span class="margin-position">[{escape_html(margin)}]</span> '
            if text:
                note_html += escape_html(text)
            for child in elem:
                note_html += process_element(child, depth + 1, margin_notes=None, endnotes=endnotes, render_semantic=render_semantic)
            note_html += '</div>\n'
            margin_notes.append(note_html)
            return escape_html(tail) if tail else ""
        classes = f"ab {escape_html(margin)} {escape_html(render)}".strip()
        html = f'<p class="{classes}" >'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</p>\n'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "hr":
        return '<hr/>\n' + escape_html(tail)
    elif tag == "lb":
        return '<br/>\n' + escape_html(tail)
    elif tag in ("pn", "pl", "pro", "m", "pa", "al", "tl", "ms", "env", "tmp", "bp", "cn", "mu", "md", "wp", "sn", "df"):
        html = f'<span class="{tag}">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag in ("la", "fr", "it", "de", "el", "oc", "po"):
        html = f'<span class="{tag}" >'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "emph":
        html = '<em>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</em>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "underline":
        html = '<u>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</u>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag in ("superscript", "sup"):
        html = '<sup>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</sup>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "del":
        html = '<del>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</del>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "add":
        html = '<ins>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</ins>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "exp":
        html = '<span class="exp">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "corr":
        html = '<span class="corr">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "ill":
        html = '<span class="ill">[illegible]</span>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "gap":
        return '<span class="gap">[gap]</span>' + escape_html(tail)
    elif tag == "mark":
        html = '<span class="mark">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html
    elif tag == "comment":
        rid = elem.get("rid", "")
        if endnotes is not None and rid:
            if rid not in [note['id'] for note in endnotes]:
                endnotes.append({'id': rid})
            note_num = next(i + 1 for i, note in enumerate(endnotes) if note['id'] == rid)
            html = f'<sup class="comment-ref"><a href="#endnote-{escape_html(rid)}" id="ref-{escape_html(rid)}">[{note_num}]</a></sup>'
            return html + escape_html(tail)
        return f'<sup class="comment-ref">[{escape_html(rid)}]</sup>' + escape_html(tail)
    elif tag == "figure":
        fig_id = elem.get("id", "")
        alt_text = elem.get("alt-text", "")
        html = f'<div class="figure" id="{escape_html(fig_id)}" >'
        html += f'<p class="figure-placeholder">[Figure: {escape_html(alt_text) if alt_text else fig_id}]</p>'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        html += '</div>\n'
        if tail:
            html += escape_html(tail)
        return html
    else:
        html = ""
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, render_semantic=render_semantic)
        if tail:
            html += escape_html(tail)
        return html

def get_css(render_semantic=False):
    """
    Generate CSS stylesheet for PDF rendering.
    """
    base_css = """
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
        font-size: 18pt;
        font-weight: bold;
        margin-top: 2em;
        margin-bottom: 1em;
        color: #2c3e50;
        border-bottom: 2px solid #2c3e50;
        padding-bottom: 0.5em;
    }

    .head.minor-head {
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

    /* Margin notes section */
    .margin-notes {
        margin-top: 1.5em;
        margin-bottom: 2em;
        padding: 1em;
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        page-break-inside: avoid;
    }

    .margin-notes-header {
        font-size: 12pt;
        font-weight: bold;
        color: #2c3e50;
        margin: 0 0 0.75em 0;
    }

    .margin-note {
        margin-bottom: 0.75em;
        padding: 0.5em;
        background-color: #ffffff;
        border-left: 2px solid #95a5a6;
        font-size: 10pt;
        line-height: 1.5;
    }

    .margin-note:last-child {
        margin-bottom: 0;
    }

    .margin-position {
        display: inline-block;
        font-weight: bold;
        color: #7f8c8d;
        font-size: 0.9em;
        font-variant: small-caps;
    }

    /* Endnotes section */
    .endnotes {
        margin-top: 3em;
        padding-top: 2em;
        border-top: 2px solid #2c3e50;
        page-break-before: always;
    }

    .endnotes-header {
        font-size: 18pt;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1em;
    }

    .endnote {
        margin-bottom: 1em;
        font-size: 10pt;
        line-height: 1.6;
        padding-left: 2em;
        text-indent: -2em;
    }

    .endnote-number {
        font-weight: bold;
        color: #3498db;
        margin-right: 0.5em;
    }

    .endnote-id {
        font-family: monospace;
        color: #7f8c8d;
        font-size: 0.85em;
        margin-right: 0.5em;
    }

    .endnote-text {
        display: block;
        margin-left: 2em;
        margin-top: 0.25em;
        color: #2c3e50;
        text-indent: 0;
    }

    .endnote-text i {
        font-style: italic;
    }

    .endnote-backlink {
        color: #3498db;
        text-decoration: none;
        font-size: 0.9em;
        margin-left: 0.5em;
    }

    .endnote-backlink:hover {
        text-decoration: underline;
    }

    /* Comment reference links */
    .comment-ref a {
        color: #3498db;
        text-decoration: none;
    }

    .comment-ref a:hover {
        text-decoration: underline;
    }
    """

    semantic_css = """
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
    """

    if render_semantic:
        return base_css + semantic_css
    else:
        return base_css

def load_comments(csv_file):
    comments = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 8:
                    comment_id, comment_text = row[2], row[7]
                    if comment_id and comment_text:
                        comments[comment_id] = comment_text
        print(f"Loaded {len(comments)} comments from CSV")
    except FileNotFoundError:
        print(f"Warning: Comment CSV not found at {csv_file}")
        print("Endnotes will only show comment IDs without content")
    except Exception as e:
        print(f"Warning: Error loading comments: {e}")
        print("Endnotes will only show comment IDs without content")
    return comments

def xml_to_html(xml_file, output_html, render_semantic=False):
    print(f"Parsing XML file: {xml_file}")
    csv_file = Path("metadata/DCE_comment-tracking-Tracking.csv")
    comments_dict = load_comments(csv_file)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    endnotes = []
    print("Converting XML to HTML...")
    body_html = process_element(root, endnotes=endnotes, render_semantic=render_semantic)
    endnotes_html = ""
    if endnotes:
        print(f"Generating {len(endnotes)} endnotes...")
        endnotes_html = '<div class="endnotes">\n'
        endnotes_html += '<h3 class="endnotes-header">Endnotes</h3>\n'
        for i, note in enumerate(endnotes, 1):
            note_id = note['id']
            comment_text = comments_dict.get(note_id, "")
            endnotes_html += f'<div class="endnote" id="endnote-{escape_html(note_id)}">\n'
            endnotes_html += f'  <span class="endnote-number">[{i}]</span>'
            endnotes_html += f'  <span class="endnote-id">{escape_html(note_id)}</span>'
            if comment_text:
                endnotes_html += f'  <span class="endnote-text">{comment_text}</span>'
            endnotes_html += f'  <a href="#ref-{escape_html(note_id)}" class="endnote-backlink">↩</a>\n'
            endnotes_html += '</div>\n'
        endnotes_html += '</div>\n'
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BnF Ms. Fr. 640 - Translation</title>
    <style>
    {get_css(render_semantic=render_semantic)}
    </style>
</head>
<body>
    <h1>Secrets of Craft and Nature in Renaissance France</h1>
    <h3>BnF Ms. Fr. 640 - English Translation</h3>
    {body_html}
    {endnotes_html}
</body>
</html>
"""
    print(f"Writing HTML to: {output_html}")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML conversion complete!")

def html_to_pdf(html_file, output_pdf):
    try:
        from weasyprint import HTML
        print(f"Generating PDF from HTML: {html_file}")
        HTML(filename=html_file).write_pdf(output_pdf)
        print(f"PDF generated successfully: {output_pdf}")
        return True
    except ImportError:
        print("\nERROR: weasyprint is not installed.")
        print("Please install it using: pip install weasyprint")
        print("\nNote: weasyprint requires additional system dependencies.")
        print("On macOS, install with: brew install python cairo pango gdk-pixbuf libffi")
        print("On Ubuntu/Debian: apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0")
        return False
    except Exception as e:
        print(f"\nERROR generating PDF: {e}")
        return False

def main():
    """
    Main entry point for the PDF generation script.
    """
    parser = argparse.ArgumentParser(description="Convert BnF Ms. Fr. 640 XML to styled PDF.")
    parser.add_argument(
        '--semantic',
        action='store_true',
        help='If set, render semantic XML elements with special styling (colors, etc.). Default is off.'
    )
    args = parser.parse_args()

    # Define input and output file paths
    xml_file = Path("allFolios/xml/tl/all_tl.xml")
    html_file = Path("allFolios/pdf/all_tl.html")
    pdf_file = Path("allFolios/pdf/all_tl.pdf")

    # Check if XML file exists
    if not xml_file.exists():
        print(f"ERROR: XML file not found: {xml_file}")
        sys.exit(1)

    # Convert XML to HTML, passing the semantic rendering flag
    xml_to_html(xml_file, html_file, render_semantic=args.semantic)

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