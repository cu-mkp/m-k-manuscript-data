#!/usr/bin/env python3
"""
BnF Ms. Fr. 640 XML to PDF Converter
=====================================

This script converts the Making and Knowing Project's XML manuscript data
(specifically the English translation version) into a formatted PDF document.

The script performs the following operations:
1. Parses the XML manuscript data
2. Converts XML elements to styled HTML with semantic formatting
3. Extracts margin notes from the manuscript and displays them separately
4. Generates a PDF using weasyprint with print-ready styling

Input:  allFolios/xml/tl/all_tl.xml (English translation)
Output: allFolios/pdf/all_tl.html (intermediate HTML)
        allFolios/pdf/all_tl.pdf (final PDF)

Author: Making and Knowing Project
Repository: https://github.com/cu-mkp/m-k-manuscript-data
"""

import xml.etree.ElementTree as ET
import sys
from pathlib import Path

# ==============================================================================
# HTML UTILITY FUNCTIONS
# ==============================================================================

def escape_html(text):
    """
    Escape HTML special characters to prevent rendering issues.

    This function converts characters that have special meaning in HTML
    (like <, >, &) into their HTML entity equivalents so they display
    correctly in the output.

    Args:
        text (str): Text to escape

    Returns:
        str: Text with HTML special characters escaped

    Example:
        >>> escape_html("A & B < C")
        'A &amp; B &lt; C'
    """
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")   # Must be first to avoid double-escaping
            .replace("<", "&lt;")     # Less than
            .replace(">", "&gt;")     # Greater than
            .replace('"', "&quot;")   # Double quote
            .replace("'", "&#39;"))   # Single quote/apostrophe

# ==============================================================================
# XML TO HTML CONVERSION
# ==============================================================================

def process_element(elem, depth=0, margin_notes=None):
    """
    Recursively process XML elements and convert to styled HTML.

    This is the core conversion function that traverses the XML tree and
    generates corresponding HTML with appropriate styling classes. It handles
    structural elements, semantic tags, language markers, and transcription
    elements according to the manuscript schema.

    Special behavior for margin notes:
    - When processing a <div>, this function collects all <ab> elements that
      have a margin attribute (e.g., margin="left-middle")
    - These margin notes are extracted from the main text flow and appended
      as a separate "Margin Notes" section after the div
    - This separates marginal annotations from the main manuscript content

    Args:
        elem (ET.Element): XML element to process
        depth (int): Current recursion depth (for debugging)
        margin_notes (list): List to collect margin note HTML strings.
                           When provided, <ab> elements with margin attributes
                           are added to this list instead of inline rendering.

    Returns:
        str: HTML representation of the element and its children
    """
    tag = elem.tag
    text = elem.text or ""  # Text content directly inside the element
    tail = elem.tail or ""  # Text that follows after the element's closing tag

    html = ""

    # ==========================================================================
    # ROOT ELEMENT: <all>
    # ==========================================================================
    # The root container for the entire manuscript
    if tag == "all":
        html = '<div class="manuscript">\n'
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</div>\n'
        return html

    # ==========================================================================
    # STRUCTURAL ELEMENTS
    # ==========================================================================

    # --------------------------------------------------------------------------
    # <div>: Text Division / Entry
    # --------------------------------------------------------------------------
    # Represents a logical section of the manuscript (an "entry" or "recipe")
    # Attributes:
    #   - id: unique identifier (e.g., "p001r_1" = page 1 recto, entry 1)
    #   - categories: semicolon-separated semantic tags (e.g., "lists;materials")
    #
    # SPECIAL BEHAVIOR: Collects margin notes from child <ab> elements and
    # displays them in a separate section after the main entry content
    elif tag == "div":
        div_id = elem.get("id", "")
        categories = elem.get("categories", "")

        # Create a list to collect margin notes for this specific div
        # Margin notes are <ab> elements with a margin attribute that appear
        # in manuscript margins (left-middle, right-top, etc.)
        div_margin_notes = []

        # Start the entry div with metadata attributes
        html = f'<div class="entry" id="{escape_html(div_id)}" data-categories="{escape_html(categories)}">\n'

        # Add any direct text content (rare in divs)
        if text.strip():
            html += escape_html(text)

        # Process all child elements, passing the margin_notes list so they
        # can add margin annotations to it
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=div_margin_notes)

        html += '</div>\n'

        # If any margin notes were collected, display them in a separate
        # styled section immediately after the entry
        if div_margin_notes:
            html += '<div class="margin-notes">\n'
            html += '<h3 class="margin-notes-header">Margin Notes:</h3>\n'
            for note_html in div_margin_notes:
                html += note_html
            html += '</div>\n'

        # Add any trailing text after the div
        if tail.strip():
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <head>: Heading / Title
    # --------------------------------------------------------------------------
    # A heading or title for an entry. Often appears at the start of a <div>.
    # Attributes:
    #   - margin: position where heading appears (e.g., "left-middle")
    #
    # Rendered as: <h2> with semantic styling
    elif tag == "head":
        margin = elem.get("margin", "")
        html = f'<h2 class="head {escape_html(margin)}">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes)
        html += '</h2>\n'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <ab>: Anonymous Block
    # --------------------------------------------------------------------------
    # A generic block of text content. The manuscript's primary text container.
    # Attributes:
    #   - margin: If present, indicates this text appears in the page margin
    #             (e.g., "left-middle", "right-top", "left-bottom")
    #   - render: Rendering hints like "wide" or "tall"
    #
    # MARGIN NOTE EXTRACTION:
    # - If margin attribute exists AND we're collecting notes (margin_notes list
    #   is provided), this <ab> is extracted and added to the margin notes
    #   section instead of appearing inline
    # - The margin position is displayed as a label (e.g., "[left-middle]")
    # - This creates a clear separation between main text and marginal annotations
    #
    # Regular <ab> elements (without margin) are rendered as <p> paragraphs
    elif tag == "ab":
        margin = elem.get("margin", "")
        render = elem.get("render", "")

        # MARGIN NOTE EXTRACTION LOGIC
        # If this ab has a margin attribute and we're collecting notes for a div,
        # extract it as a margin note instead of rendering it inline
        if margin and margin_notes is not None:
            note_html = f'<div class="margin-note" data-position="{escape_html(margin)}">\n'
            # Add position label (e.g., "[left-middle]")
            note_html += f'<span class="margin-position">[{escape_html(margin)}]</span> '
            if text:
                note_html += escape_html(text)
            # Process children but don't collect more notes (margin_notes=None)
            for child in elem:
                note_html += process_element(child, depth + 1, margin_notes=None)
            note_html += '</div>\n'
            # Add to the parent div's margin notes collection
            margin_notes.append(note_html)

            # Return only the tail text (the margin note itself is now collected)
            return escape_html(tail) if tail else ""

        # Regular ab without margin: render as paragraph
        classes = f"ab {escape_html(margin)} {escape_html(render)}".strip()
        html = f'<p class="{classes}">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes)
        html += '</p>\n'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <hr>: Horizontal Rule
    # --------------------------------------------------------------------------
    # A horizontal line separator in the manuscript
    elif tag == "hr":
        return '<hr/>\n' + escape_html(tail)

    # --------------------------------------------------------------------------
    # <lb>: Line Break
    # --------------------------------------------------------------------------
    # Marks the end of a line in the source manuscript
    elif tag == "lb":
        return '<br/>\n' + escape_html(tail)

    # ==========================================================================
    # SEMANTIC ELEMENTS
    # ==========================================================================
    # These elements mark up significant terms and concepts in the manuscript.
    # Each is rendered as a <span> with a specific CSS class that applies
    # distinct styling (colors, weights) to make different categories visually
    # distinguishable.
    #
    # The Making and Knowing Project uses these tags to enable semantic search
    # and analysis of the manuscript content.

    # --------------------------------------------------------------------------
    # <pn>: Personal Name
    # --------------------------------------------------------------------------
    # Names of people mentioned in the manuscript
    # Styling: Bold, teal color (#16a085)
    # Examples: Mestre Jehan Cousin, Bernard Palissi, Alexander Aphrodisæus
    elif tag == "pn":
        html = '<span class="pn">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <pl>: Place
    # --------------------------------------------------------------------------
    # Geographical locations and place names
    # Styling: Medium weight, blue color (#2980b9)
    # Examples: Rue de la Heaumerie, Faubourg Saint-Germain, Lyon
    elif tag == "pl":
        html = '<span class="pl">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <pro>: Profession
    # --------------------------------------------------------------------------
    # Occupations, trades, and professional roles
    # Styling: Small caps, purple color (#8e44ad)
    # Examples: master, harvester, currier, inventor
    elif tag == "pro":
        html = '<span class="pro">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <m>: Material
    # --------------------------------------------------------------------------
    # Substances and materials used in craft processes
    # Styling: Orange color (#d35400)
    # Examples: sand, oil, wax. May contain nested <pa> (plant) tags
    elif tag == "m":
        html = '<span class="m">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <pa>: Plant
    # --------------------------------------------------------------------------
    # Plant names and botanical references
    # Styling: Green color (#27ae60)
    # Examples: pastel woad flowers, oak, rose
    elif tag == "pa":
        html = '<span class="pa">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <al>: Animal
    # --------------------------------------------------------------------------
    # Animal names and references
    # Styling: Red color (#c0392b)
    # Examples: horse, falcon, fish
    elif tag == "al":
        html = '<span class="al">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <tl>: Tool
    # --------------------------------------------------------------------------
    # Tools and implements used in craft processes
    # Styling: Gray color (#7f8c8d)
    # Examples: mold, hammer, furnace
    elif tag == "tl":
        html = '<span class="tl">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <ms>: Measurement
    # --------------------------------------------------------------------------
    # Quantities and measurements
    # Styling: Monospace font
    # Examples: one pound, three fingers, half an ounce
    elif tag == "ms":
        html = '<span class="ms">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # --------------------------------------------------------------------------
    # <env>: Environment
    # --------------------------------------------------------------------------
    # Physical spaces and environmental references
    # Styling: Teal color (#16a085)
    # Examples: workshop, mountains, forest
    elif tag == "env":
        html = '<span class="env">'
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1)
        html += '</span>'
        if tail:
            html += escape_html(tail)
        return html

    # Additional semantic elements (all rendered as styled <span> elements):
    # <tmp>: Temporal terms (time references) - italic, gray
    # <bp>: Body parts - red
    # <cn>: Currency terms - orange/gold
    # <mu>: Musical instruments - purple
    # <md>: Medical terms - orange
    # <wp>: Weapons - red
    # <sn>: Sense terms (sensory descriptions) - italic
    # <df>: Definitions - medium weight

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

    # ==========================================================================
    # LANGUAGE ELEMENTS
    # ==========================================================================
    # These mark text in languages other than the primary language (English
    # translation). All language elements are rendered in italics to
    # distinguish them from English text.
    #
    # Supported languages:
    # <la>: Latin (most common) - italic, dark gray
    # <fr>: French - italic
    # <it>: Italian - italic
    # <de>: German - italic
    # <el>: Greek - italic
    # <oc>: Occitan - italic
    # <po>: Poitevin (dialect) - italic

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

    # ==========================================================================
    # TRANSCRIPTION ELEMENTS
    # ==========================================================================
    # These elements record editorial interventions and manuscript features
    # related to the transcription process. They preserve information about
    # how the original manuscript text was written and modified.
    #
    # Elements:
    # <emph>: Emphasized text in original - rendered as italic
    # <underline>: Underlined text in original - rendered as underlined
    # <sup> / <superscript>: Superscript or supplied text - rendered as superscript
    # <del>: Deleted text in original - rendered with strikethrough
    # <add>: Added text in original - rendered with dotted underline
    # <exp>: Abbreviated text expanded by editor - normal rendering
    # <corr>: Editor correction - blue color
    # <ill>: Illegible text in original - gray, italic, shows "[illegible]"
    # <gap>: Gap in manuscript - gray, italic, shows "[gap]"
    # <mark>: Symbols in original - bold, red

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
            html += process_element(child, depth + 1, margin_notes=margin_notes)
        html += '</div>\n'
        if tail:
            html += escape_html(tail)
        return html

    # ==========================================================================
    # DEFAULT HANDLER
    # ==========================================================================
    # For any unrecognized elements, process their text and children
    # This ensures the conversion doesn't fail on unexpected elements
    else:
        html = ""
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes)
        if tail:
            html += escape_html(tail)
        return html

# ==============================================================================
# CSS STYLING
# ==============================================================================

def get_css():
    """
    Generate CSS stylesheet for PDF rendering.

    This function returns a comprehensive CSS stylesheet that:
    - Sets up print-friendly page layout (US Letter, 1" margins)
    - Defines typography using classic serif fonts (Garamond, Georgia)
    - Applies semantic color-coding to different element types
    - Styles margin notes sections with distinct visual treatment
    - Ensures proper page breaks for entries
    - Creates a readable, professional manuscript presentation

    The color scheme uses muted, distinct colors to make different semantic
    categories easily distinguishable while maintaining readability in print.

    Returns:
        str: Complete CSS stylesheet as a string
    """
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
    """

# ==============================================================================
# CONVERSION PIPELINE FUNCTIONS
# ==============================================================================

def xml_to_html(xml_file, output_html):
    """
    Convert manuscript XML file to styled HTML.

    This function orchestrates the XML-to-HTML conversion process:
    1. Parses the XML manuscript file using ElementTree
    2. Recursively processes all elements via process_element()
    3. Wraps the converted content in a complete HTML document
    4. Embeds the CSS stylesheet for styling
    5. Writes the final HTML to disk

    The resulting HTML file can be viewed in a browser or converted to PDF.
    It includes:
    - Document title and metadata
    - Embedded CSS for all styling
    - Manuscript title headers
    - All converted manuscript content with semantic formatting
    - Extracted margin notes in separate sections

    Args:
        xml_file (Path): Path to input XML file (all_tl.xml)
        output_html (Path): Path where HTML output should be written

    Output:
        Creates an HTML file with UTF-8 encoding containing the formatted
        manuscript content
    """
    print(f"Parsing XML file: {xml_file}")

    # Parse the XML manuscript file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Convert XML tree to HTML by recursively processing all elements
    print("Converting XML to HTML...")
    body_html = process_element(root)

    # Create complete HTML document with metadata, styling, and content
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

    # Write HTML to file with UTF-8 encoding
    print(f"Writing HTML to: {output_html}")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print("HTML conversion complete!")

def html_to_pdf(html_file, output_pdf):
    """
    Convert HTML file to PDF using weasyprint library.

    This function uses the weasyprint library to render the HTML as a PDF
    with proper pagination, fonts, and styling. Weasyprint is a CSS-based
    PDF renderer that supports modern web standards.

    The function handles:
    - Loading and parsing the HTML file
    - Rendering CSS styles (including @page rules for print layout)
    - Generating a print-ready PDF with proper fonts and formatting
    - Error handling for missing dependencies

    Args:
        html_file (Path): Path to input HTML file
        output_pdf (Path): Path where PDF should be written

    Returns:
        bool: True if PDF generation succeeded, False otherwise

    Dependencies:
        Requires weasyprint and system libraries (cairo, pango, etc.)
        See function output for installation instructions if missing
    """
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
    """
    Main entry point for the PDF generation script.

    This function coordinates the complete conversion pipeline:
    1. Defines input/output file paths
    2. Validates that the input XML file exists
    3. Converts XML to HTML
    4. Converts HTML to PDF (if weasyprint is available)
    5. Reports results to user

    File paths:
    - Input:  allFolios/xml/tl/all_tl.xml (English translation XML)
    - Output: allFolios/pdf/all_tl.html (intermediate HTML)
    - Output: allFolios/pdf/all_tl.pdf (final PDF)

    Exit codes:
        0: Success
        1: Input file not found

    Usage:
        Run from repository root: python3 lib/generate_pdf.py
        Or with venv: source .venv/bin/activate && python3 lib/generate_pdf.py
    """
    # Define input and output file paths
    xml_file = Path("allFolios/xml/tl/all_tl.xml")
    html_file = Path("allFolios/pdf/all_tl.html")
    pdf_file = Path("allFolios/pdf/all_tl.pdf")

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
