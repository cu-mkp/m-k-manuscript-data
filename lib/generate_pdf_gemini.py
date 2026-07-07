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
import re
import argparse
from pathlib import Path
import urllib.request
from collections import defaultdict

def create_figure_list_html(figures):
    """
    Creates the HTML for a list of figures.
    """
    if not figures:
        return ""

    html = '<div id="list-of-figures" style="page-break-before: always;">\n'
    html += '<h2>List of Figures</h2>\n'
    for fig in figures:
        html += f'<div class="figure-list-item" id="figure-list-{escape_html(fig["id"])}">\n'
        html += f'<img src="../../images/{escape_html(fig["local_path"].name)}" alt="{escape_html(fig["alt_text"])}">\n'
        html += f'<p class="figure-caption">Figure {escape_html(fig["id"].replace("fig_", ""))} - {escape_html(fig["alt_text"])}</p>\n'
        html += f'<a href="#{escape_html(fig["id"])}">Back to reference</a>\n'
        html += '</div>\n'
    html += '</div>\n'
    return html

def create_toc_html():
    """
    Creates the HTML for a table of contents.
    """
    html = """
    <div class="toc" style="page-break-after: always;">
        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#transcription">Transcription</a></li>
            <li><a href="#endnotes">Endnotes</a></li>
            <li><a href="#back-of-book-index">Index of Categories</a></li>
            <li><a href="#tag-index">Index of Tags</a></li>
            <li><a href="#essay-index">Index of Essays</a></li>
            <li><a href="#list-of-figures">List of Figures</a></li>
        </ul>
    </div>
    """
    return html

def create_title_page_html():
    """
    Creates the HTML for a title page.
    """
    html = """
    <div class="title-page">
        <h1>Secrets of Craft and Nature in Renaissance France</h1>
        <h2>A Digital Critical Edition and English Translation of BnF Ms. Fr. 640</h2>
        <div class="publishers">
            <p><strong>Edited by:</strong></p>
            <p>The Making and Knowing Project, Pamela H. Smith, Naomi Rosenkranz, Tianna Helena Uchacz, Tillmann Taape, Clément Godbarge, Sophie Pitman, Jenny Boulboullé, Joel Klein, Donna Bilak, Marc Smith, and Terry Catapano</p>
        </div>
        <div class="publication-info">
            <p>New York: Making and Knowing Project, 2020</p>
            <p><a href="https://edition640.makingandknowing.org">https://edition640.makingandknowing.org</a></p>
        </div>
    </div>
    """
    return html

def create_index_html(root):
    """
    Creates a back-of-book style index from the div categories attributes in the XML tree.
    """
    index = defaultdict(list)
    for div in root.iter('div'):
        categories_attr = div.get('categories', '').strip()
        if not categories_attr:
            continue
        head = div.find('head')
        if head is None:
            continue
        heading = ''.join(head.itertext()).strip()
        if not heading:
            continue
        div_id = div.get('id', '')
        folio_match = re.match(r'p(\d+[rv])', div_id)
        folio = folio_match.group(1) if folio_match else div_id
        entry = f"<a href=\"#{escape_html(div_id)}\">{escape_html(heading)} ({escape_html(folio)})</a>"
        for category in categories_attr.split(';'):
            category = category.strip()
            if category:
                index[category].append(entry)

    html = '<div id="back-of-book-index" style="page-break-before: always;">\n'
    html += '<h2>Index of Categories</h2>\n'
    for category in sorted(index.keys()):
        html += f"<h3>{escape_html(category.capitalize())}</h3>\n"
        html += "<ul>\n"
        for entry in sorted(index[category]):
            html += f"<li>{entry}</li>\n"
        html += "</ul>\n"
    html += '</div>\n'
    return html

# Semantic phrase-level tags to index, mapped to display labels.
# Language/dialect tags (fr, la, gk, it, oc, po) and editorial markup are
# deliberately excluded. Labels follow vocabulary/README.md and the schema docs.
TAG_INDEX_TYPES = {
    'al': 'Animals',
    'bp': 'Body parts',
    'cn': 'Coins and currency',
    'df': 'Definitions',
    'env': 'Environments and physical spaces',
    'm': 'Materials',
    'md': 'Medical',
    'ms': 'Measurements',
    'mu': 'Music',
    'pa': 'Plants',
    'pl': 'Places',
    'pn': 'Personal names',
    'pro': 'Professions',
    'sn': 'Sensory',
    'tl': 'Tools',
    'tmp': 'Time and temporal',
    'wp': 'Weapons',
}

def folio_label(div_id):
    """p003r_1 -> 3r; falls back to the raw id."""
    m = re.match(r'p0*(\d+)([rv])', div_id)
    return f"{m.group(1)}{m.group(2)}" if m else div_id

def folio_sort_key(div_id):
    """Manuscript-order sort key for entry div ids like p003r_1."""
    m = re.match(r'p0*(\d+)([rv])_?(\d*)', div_id)
    if not m:
        return (9999, 2, 0)
    return (int(m.group(1)), 0 if m.group(2) == 'r' else 1, int(m.group(3) or 0))

def tag_term_text(elem):
    """Collect an element's text for indexing: skip deleted text, collapse whitespace."""
    parts = []
    def walk(e):
        if e.tag == 'del':
            return
        if e.text:
            parts.append(e.text)
        for child in e:
            walk(child)
            if child.tail:
                parts.append(child.tail)
    walk(elem)
    term = re.sub(r'\s+', ' ', ''.join(parts)).strip().strip(',;:.')
    return term

def create_tag_index_html(root):
    """
    Creates an index of semantic tags: for each tag type, unique terms in
    alphabetical order, each with links to the folios of entries where the
    term occurs.
    """
    parent_map = {child: p for p in root.iter() for child in p}

    def enclosing_div_id(elem):
        node = elem
        while node is not None:
            if node.tag == 'div' and node.get('id'):
                return node.get('id')
            node = parent_map.get(node)
        return None

    # tag type -> casefolded term -> {'forms': Counter, 'divs': set}
    index = {t: defaultdict(lambda: {'forms': defaultdict(int), 'divs': set()})
             for t in TAG_INDEX_TYPES}
    for tag_type in TAG_INDEX_TYPES:
        for elem in root.iter(tag_type):
            term = tag_term_text(elem)
            if not term:
                continue
            div_id = enclosing_div_id(elem)
            if not div_id:
                continue
            slot = index[tag_type][term.casefold()]
            slot['forms'][term] += 1
            slot['divs'].add(div_id)

    html = '<div id="tag-index" class="tag-index" style="page-break-before: always;">\n'
    html += '<h2>Index of Tags</h2>\n'
    html += ('<p class="index-note">Terms marked in the manuscript, by tag type. '
             'Each reference links to the first entry on that folio containing the term.</p>\n')
    for tag_type, label in sorted(TAG_INDEX_TYPES.items(), key=lambda kv: kv[1]):
        terms = index[tag_type]
        if not terms:
            continue
        html += f'<h3 class="tag-index-type">{escape_html(label)}</h3>\n'
        html += '<ul class="tag-index-terms">\n'
        for key in sorted(terms.keys()):
            slot = terms[key]
            # display the most frequent surface form of the term
            display = max(slot['forms'].items(), key=lambda kv: kv[1])[0]
            # one link per folio: first entry on the folio (manuscript order)
            by_folio = {}
            for div_id in sorted(slot['divs'], key=folio_sort_key):
                by_folio.setdefault(folio_label(div_id), div_id)
            links = ', '.join(
                f'<a href="#{escape_html(div_id)}">{escape_html(fol)}</a>'
                for fol, div_id in by_folio.items()
            )
            html += f'<li>{escape_html(display)}&ensp;{links}</li>\n'
        html += '</ul>\n'
    html += '</div>\n'
    return html

def create_essay_index_html(root, csv_file):
    """
    Creates an index of edition essays grouped by the manuscript entry they
    discuss, from metadata/annotation-metadata.csv. Entry headings link to the
    entry in this document; essay titles link to the online edition.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Warning: annotation metadata CSV not found at {csv_file}; skipping essay index")
        return ""

    headings = {}
    known_ids = set()
    for div in root.iter('div'):
        div_id = div.get('id')
        if not div_id:
            continue
        known_ids.add(div_id)
        head = div.find('head')
        if head is not None:
            text = re.sub(r'\s+', ' ', ''.join(head.itertext())).strip()
            if text:
                headings[div_id] = text

    def normalize_entry_id(raw):
        """Repair common entry-id format slips (missing 'p', unpadded folio)."""
        eid = raw.strip()
        if eid in known_ids:
            return eid
        m = re.match(r'p?0*(\d+)([rv])_(\w+)$', eid)
        if m:
            candidate = f'p{int(m.group(1)):03d}{m.group(2)}_{m.group(3)}'
            if candidate in known_ids:
                return candidate
        return None

    by_entry = defaultdict(list)
    unlinked = []
    unmatched_ids = set()
    for row in rows:
        title = row.get('full-title', '').strip()
        if not title:
            continue
        essay = {
            'title': title,
            'authors': row.get('author', '').strip(),
            'url': row.get('edition-URL', '').strip(),
        }
        entry_ids = [e.strip() for e in row.get('entry-id', '').split(';') if e.strip()]
        if entry_ids:
            for entry_id in entry_ids:
                normalized = normalize_entry_id(entry_id)
                if normalized:
                    by_entry[normalized].append(essay)
                else:
                    unmatched_ids.add(entry_id)
                    unlinked.append(essay)
        else:
            unlinked.append(essay)
    if unmatched_ids:
        print(f"Warning: essay index: entry-ids not found in XML (listed without links): "
              f"{sorted(unmatched_ids)} — fix in metadata/annotation-metadata.csv")

    def essay_item_html(essay):
        title_html = escape_html(essay['title'])
        if essay['url']:
            title_html = f'<a href="{escape_html(essay["url"])}">{title_html}</a>'
        authors = f' — {escape_html(essay["authors"])}' if essay['authors'] else ''
        return f'<li>{title_html}{authors}</li>\n'

    html = '<div id="essay-index" class="essay-index" style="page-break-before: always;">\n'
    html += '<h2>Index of Essays</h2>\n'
    html += ('<p class="index-note">Research essays from the online edition, by the '
             'manuscript entry they discuss. Essay titles link to the edition; entry '
             'headings link to the entry in this document.</p>\n')
    for entry_id in sorted(by_entry.keys(), key=folio_sort_key):
        heading = headings.get(entry_id, entry_id)
        html += (f'<h4 class="essay-index-entry"><a href="#{escape_html(entry_id)}">'
                 f'{escape_html(heading)} ({escape_html(folio_label(entry_id))})</a></h4>\n')
        html += '<ul class="essay-index-essays">\n'
        for essay in sorted(by_entry[entry_id], key=lambda e: e['title']):
            html += essay_item_html(essay)
        html += '</ul>\n'
    if unlinked:
        # dedupe essays that ended up here via multiple unmatched ids
        seen = set()
        unlinked = [e for e in unlinked
                    if not (e['title'] in seen or seen.add(e['title']))]
        html += '<h4 class="essay-index-entry">Not linked to a specific entry</h4>\n'
        html += '<ul class="essay-index-essays">\n'
        for essay in sorted(unlinked, key=lambda e: e['title']):
            html += essay_item_html(essay)
        html += '</ul>\n'
    html += '</div>\n'
    return html

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

def process_element(elem, depth=0, margin_notes=None, endnotes=None, figures=None, render_semantic=False):

    """

    Recursively process XML elements and convert to styled HTML.

    """

    tag = elem.tag

    text = elem.text or ""

    tail = elem.tail or ""

    html = ""



    if tag == "all":

        html = '<div class="manuscript" id="transcription">\n'

        for child in elem:

            html += process_element(child, depth + 1, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

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

            html += process_element(child, depth + 1, margin_notes=div_margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</div>\n'

        if div_margin_notes:

            html += '<div class="margin-notes">\n'

            html += '<p class="margin-notes-header">in margin:</p>\n'

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

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

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

                note_html += process_element(child, depth + 1, margin_notes=None, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

            note_html += '</div>\n'

            margin_notes.append(note_html)

            return escape_html(tail) if tail else ""

        classes = f"ab {escape_html(margin)} {escape_html(render)}".strip()

        html = f'<p class="{classes}" >'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

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

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</span>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag in ("la", "fr", "it", "de", "el", "oc", "po"):

        html = f'<span class="{tag}" >'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</span>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "emph":

        html = '<em>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</em>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "underline":

        html = '<u>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</u>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag in ("superscript", "sup"):

        html = '<sup>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</sup>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "del":

        html = '<del>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</del>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "add":

        html = '<ins>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</ins>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "exp":

        html = '<span class="exp">'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</span>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "corr":

        html = '<span class="corr">'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</span>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "ill":

        html = '<span class="ill">[illegible]</span>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

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

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</span>'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "comment":
        rid = elem.get("rid", "")
        if endnotes is not None and rid:
            note = next((n for n in endnotes if n['id'] == rid), None)
            if note is None:
                note = {'id': rid, 'refs': []}
                endnotes.append(note)
            note_num = endnotes.index(note) + 1
            ref_count = len(note['refs']) + 1
            ref_id = f"ref-{rid}-{ref_count}"
            note['refs'].append(ref_id)
            html = f'<sup class="comment-ref"><a href="#endnote-{escape_html(rid)}" id="{escape_html(ref_id)}">[{note_num}]</a></sup>'
            return html + escape_html(tail)
        return f'<sup class="comment-ref">[{escape_html(rid)}]</sup>' + escape_html(tail)
    elif tag == "figure":
        fig_id = elem.get("id", "")
        alt_text = elem.get("alt-text", "")
        
        if figures is not None:
            # Construct the image URL and local path
            base_url = "https://edition-assets.makingandknowing.org/manuscript-figures/"
            img_filename = fig_id.replace("fig_", "") + ".png"
            img_url = base_url + img_filename
            local_img_path = Path("../images") / img_filename

            # Download the image if it doesn't exist
            if not local_img_path.exists():
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(local_img_path, 'wb') as out_file:
                        data = response.read()
                        out_file.write(data)
                    print(f"Downloaded {img_url} to {local_img_path}")
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")

            # Add figure info to the list for later use
            figures.append({
                "id": fig_id,
                "alt_text": alt_text,
                "local_path": local_img_path
            })
            
                            # Create a link to the figure in the list of figures
            html = f'<a id="{escape_html(fig_id)}" href="#figure-list-{escape_html(fig_id)}">[Figure: {escape_html(alt_text) if alt_text else fig_id}]</a>'
        else:
            # Fallback for when figures are not being processed
            html = f'<div class="figure" id="{escape_html(fig_id)}" >'
            html += f'<p class="figure-placeholder">[Figure: {escape_html(alt_text) if alt_text else fig_id}]</p>'

        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)
        
        if figures is None:
            html += '</div>\n'

        if tail:
            html += escape_html(tail)
        return html
    else:
        html = ""
        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)
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

    /* PDF outline bookmarks */
    h1 {
        bookmark-level: 1;
        bookmark-label: content();
    }
    h2 {
        bookmark-level: 1;
        bookmark-label: content();
    }
    h3.head:not(.minor-head) {
        bookmark-level: 2;
        bookmark-label: content();
    }
    h3.head.minor-head {
        bookmark-level: 3;
        bookmark-label: content();
    }
    h3.tag-index-type {
        bookmark-level: 2;
        bookmark-label: content();
    }

    /* Back-matter indexes */
    .index-note {
        font-style: italic;
        font-size: 9pt;
        color: #555;
    }
    ul.tag-index-terms {
        columns: 2;
        column-gap: 2em;
        list-style: none;
        margin: 0 0 1em 0;
        padding: 0;
        font-size: 9pt;
    }
    ul.tag-index-terms li {
        break-inside: avoid;
        margin-bottom: 0.15em;
    }
    h4.essay-index-entry {
        margin: 0.8em 0 0.2em 0;
    }
    ul.essay-index-essays {
        margin: 0 0 0.5em 0;
        font-size: 10pt;
    }

    .title-page {
        border: 1px solid black;
        padding: 2em;
        text-align: center;
        height: 8.5in;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .title-page h1 {
        font-size: 24pt;
        margin-bottom: 0.5em;
    }

    .title-page h2 {
        font-size: 18pt;
        margin-bottom: 2em;
    }

    .publishers {
        margin-bottom: 2em;
    }

    .publication-info {
        font-style: italic;
    }

    .figure-list-item {
        margin-bottom: 2em;
        page-break-inside: avoid;
    }

    .figure-list-item img {
        max-width: 100%;
        height: auto;
    }

    .figure-caption {
        font-size: 10pt;
        font-style: italic;
        margin-top: 0.5em;
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

    /* In margin section */
    .margin-notes {
        margin-top: 1.5em;
        margin-bottom: 2em;
        padding: 1em;
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        page-break-inside: avoid;
    }

    .margin-notes-header {
        font-size: 10pt;
        font-weight: normal;
        color: #7f8c8d;
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

import urllib.request
def xml_to_html(xml_file, output_html, render_semantic=False):
    print(f"Parsing XML file: {xml_file}")
    csv_file = Path("../metadata/DCE_comment-tracking-Tracking.csv")
    comments_dict = load_comments(csv_file)
    Path("../images").mkdir(exist_ok=True)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    endnotes = []
    figures = []
    print("Converting XML to HTML...")
    body_html = process_element(root, endnotes=endnotes, figures=figures, render_semantic=render_semantic)
    index_html = create_index_html(root)
    tag_index_html = create_tag_index_html(root)
    essay_index_html = create_essay_index_html(root, Path("../metadata/annotation-metadata.csv"))
    title_page_html = create_title_page_html()
    toc_html = create_toc_html()
    figure_list_html = create_figure_list_html(figures)
    endnotes_html = ""
    if endnotes:
        print(f"Generating {len(endnotes)} endnotes...")
        endnotes_html = '<div class="endnotes" id="endnotes">\n'
        endnotes_html += '<h3 class="endnotes-header">Endnotes</h3>\n'
        for i, note in enumerate(endnotes, 1):
            note_id = note['id']
            refs = note.get('refs', [])
            comment_text = comments_dict.get(note_id, "")
            endnotes_html += f'<div class="endnote" id="endnote-{escape_html(note_id)}">\n'
            endnotes_html += f'  <span class="endnote-number">[{i}]</span>'
            endnotes_html += f'  <span class="endnote-id">{escape_html(note_id)}</span>'
            if comment_text:
                endnotes_html += f'  <span class="endnote-text">{comment_text}</span>'
            if len(refs) > 1:
                for j, ref_id in enumerate(refs, 1):
                    endnotes_html += f'  <a href="#{escape_html(ref_id)}" class="endnote-backlink">↩{j}</a>'
            elif refs:
                endnotes_html += f'  <a href="#{escape_html(refs[0])}" class="endnote-backlink">↩</a>'
            endnotes_html += '\n</div>\n'
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
    {title_page_html}
    {toc_html}
    <h1>Secrets of Craft and Nature in Renaissance France</h1>
    <h3>BnF Ms. Fr. 640 - English Translation</h3>
    {body_html}
    {endnotes_html}
    {index_html}
    {tag_index_html}
    {essay_index_html}
    {figure_list_html}
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

    # Define input and output file paths; the semantic rendering gets its own
    # output files so the two variants can coexist
    xml_file = Path("../allFolios/xml/tl/all_tl.xml")
    suffix = "_semantic" if args.semantic else ""
    html_file = Path(f"../allFolios/pdf/all_tl{suffix}.html")
    pdf_file = Path(f"../allFolios/pdf/all_tl{suffix}.pdf")

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