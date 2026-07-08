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


# ==============================================================================
# VERSIONS AND LABELS
# ==============================================================================

# Which manuscript version is being rendered, and in which language its
# generated apparatus (titles, index headings, notes) is written.
# tl  = English translation; tc = diplomatic French transcription;
# tcn = normalized French transcription.
VERSION_LANG = {'tl': 'en', 'tc': 'fr', 'tcn': 'fr'}

LABELS = {
    'en': {
        'toc': 'Table of Contents',
        'text_section': 'Translation',
        'subtitle': 'BnF Ms. Fr. 640 &mdash; English Translation',
        'title_page_subtitle': 'A Digital Critical Edition and English Translation of BnF Ms. Fr. 640',
        'edited_by': 'Edited by:',
        'publication': 'New York: Making and Knowing Project, 2020',
        'endnotes': 'Endnotes',
        'index_categories': 'Index of Categories',
        'index_tags': 'Index of Tags',
        'index_essays': 'Index of Essays',
        'list_of_figures': 'List of Figures',
        'back_to_reference': 'Back to reference',
        'figure': 'Figure',
        'in_margin': 'in margin:',
        'essay': 'essay',
        'essays': 'essays',
        'see_essays': 'See {n} on this entry',
        'tag_index_note': ('Terms marked in the manuscript, by tag type. '
                           'Each reference links to the first entry on that folio containing the term.'),
        'essay_index_note': ('Research essays from the online edition, by the manuscript entry they '
                             'discuss. Essay titles link to the edition; entry headings link to the '
                             'entry in this document.'),
        'general_essays': 'General essays on the manuscript and edition',
        'folio_range_title': 'Folio range of this entry',
        'illegible': '[illegible]',
        'gap': '[gap]',
        'figure_ref': '[Figure: {label}]',
    },
    'fr': {
        'toc': 'Table des matières',
        'text_section': 'Transcription normalisée',
        'subtitle': 'BnF Ms. Fr. 640 &mdash; Transcription normalisée',
        'title_page_subtitle': 'Édition critique numérique du BnF Ms. Fr. 640 &mdash; transcription normalisée',
        'edited_by': 'Édité par :',
        'publication': 'New York : Making and Knowing Project, 2020',
        'endnotes': 'Notes',
        'index_categories': 'Index des catégories',
        'index_tags': 'Index des termes balisés',
        'index_essays': 'Index des essais',
        'list_of_figures': 'Liste des figures',
        'back_to_reference': 'Retour à la référence',
        'figure': 'Figure',
        'in_margin': 'en marge :',
        'essay': 'essai',
        'essays': 'essais',
        'see_essays': 'Voir {n} sur cette entrée',
        'tag_index_note': ('Termes balisés dans le manuscrit, par type de balise. Chaque référence '
                           'renvoie à la première entrée du folio où le terme apparaît.'),
        'essay_index_note': ('Essais de l’édition en ligne, classés par l’entrée du manuscrit qu’ils '
                             'traitent. Les titres renvoient à l’édition en ligne ; les intitulés '
                             'd’entrée renvoient à l’entrée dans ce document.'),
        'general_essays': 'Essais généraux sur le manuscrit et l’édition',
        'folio_range_title': 'Étendue en folios de cette entrée',
        'illegible': '[illisible]',
        'gap': '[lacune]',
        'figure_ref': '[Figure : {label}]',
    },
}

# Semantic tag-type labels per language (keys are the XML element names).
TAG_LABELS = {
    'en': {
        'al': 'Animals', 'bp': 'Body parts', 'cn': 'Coins and currency',
        'df': 'Definitions', 'env': 'Environments and physical spaces',
        'm': 'Materials', 'md': 'Medical', 'ms': 'Measurements', 'mu': 'Music',
        'pa': 'Plants', 'pl': 'Places', 'pn': 'Personal names',
        'pro': 'Professions', 'sn': 'Sensory', 'tl': 'Tools',
        'tmp': 'Time and temporal', 'wp': 'Weapons',
    },
    'fr': {
        'al': 'Animaux', 'bp': 'Parties du corps', 'cn': 'Monnaies',
        'df': 'Définitions', 'env': 'Environnements et espaces physiques',
        'm': 'Matériaux', 'md': 'Médical', 'ms': 'Mesures', 'mu': 'Musique',
        'pa': 'Plantes', 'pl': 'Lieux', 'pn': 'Noms de personnes',
        'pro': 'Métiers', 'sn': 'Sensoriel', 'tl': 'Outils',
        'tmp': 'Temps', 'wp': 'Armes',
    },
}

# Manuscript margin positions (the `margin` attribute value), rendered as the
# label on a margin note. English keeps the source values; French translates.
POSITION_LABELS = {
    'en': {},   # empty -> the raw attribute value is used
    'fr': {
        'left-top': 'marge gauche, en haut',
        'left-middle': 'marge gauche, au milieu',
        'left-bottom': 'marge gauche, en bas',
        'right-top': 'marge droite, en haut',
        'right-middle': 'marge droite, au milieu',
        'right-bottom': 'marge droite, en bas',
        'top': 'en haut',
        'bottom': 'en bas',
    },
}

def position_label(margin):
    """Human-readable label for a margin position, in the current language."""
    return POSITION_LABELS[LANG].get(margin, margin)

# Populated by main()/xml_to_html for the version being rendered.
LANG = 'en'
L = LABELS['en']
TAG_INDEX_TYPES = dict(TAG_LABELS['en'])

def set_language(version):
    """Point the module's label tables at the language of this version."""
    global LANG, L
    LANG = VERSION_LANG.get(version, 'en')
    L = LABELS[LANG]
    TAG_INDEX_TYPES.clear()
    TAG_INDEX_TYPES.update(TAG_LABELS[LANG])

def create_figure_list_html(figures):
    """
    Creates the HTML for a list of figures.
    """
    if not figures:
        return ""

    html = '<div id="list-of-figures" style="page-break-before: always;">\n'
    html += f'<h2>{escape_html(L["list_of_figures"])}</h2>\n'
    for fig in figures:
        html += f'<div class="figure-list-item" id="figure-list-{escape_html(fig["id"])}">\n'
        html += f'<img src="../../images/{escape_html(fig["local_path"].name)}" alt="{escape_html(fig["alt_text"])}">\n'
        html += (f'<p class="figure-caption">{escape_html(L["figure"])} '
                 f'{escape_html(fig["id"].replace("fig_", ""))} - {escape_html(fig["alt_text"])}</p>\n')
        html += f'<a href="#{escape_html(fig["id"])}">{escape_html(L["back_to_reference"])}</a>\n'
        html += '</div>\n'
    html += '</div>\n'
    return html

def create_toc_html(include_figure_list=True):
    """
    Creates the HTML for a table of contents.
    """
    figure_list_item = (f'            <li><a href="#list-of-figures">{escape_html(L["list_of_figures"])}</a></li>\n'
                        if include_figure_list else '')
    html = f"""
    <div class="toc" style="page-break-after: always;">
        <h2>{escape_html(L["toc"])}</h2>
        <ul>
            <li><a href="#translation">{escape_html(L["text_section"])}</a></li>
            <li><a href="#endnotes">{escape_html(L["endnotes"])}</a></li>
            <li><a href="#back-of-book-index">{escape_html(L["index_categories"])}</a></li>
            <li><a href="#tag-index">{escape_html(L["index_tags"])}</a></li>
            <li><a href="#essay-index">{escape_html(L["index_essays"])}</a></li>
{figure_list_item}        </ul>
    </div>
    """
    return html

def create_title_page_html():
    """
    Creates the HTML for a title page.
    """
    html = f"""
    <div class="title-page">
        <h1>Secrets of Craft and Nature in Renaissance France</h1>
        <h2>{L["title_page_subtitle"]}</h2>
        <div class="publishers">
            <p><strong>{L["edited_by"]}</strong></p>
            <p>The Making and Knowing Project, Pamela H. Smith, Naomi Rosenkranz, Tianna Helena Uchacz, Tillmann Taape, Clément Godbarge, Sophie Pitman, Jenny Boulboullé, Joel Klein, Donna Bilak, Marc Smith, and Terry Catapano</p>
        </div>
        <div class="publication-info">
            <p>{L["publication"]}</p>
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
        folio = folio_range_label(div_id)
        entry = f"<a href=\"#{escape_html(div_id)}\">{escape_html(heading)} (fol. {escape_html(folio)})</a>"
        for category in categories_attr.split(';'):
            category = category.strip()
            if category:
                index[category].append(entry)

    html = '<div id="back-of-book-index" style="page-break-before: always;">\n'
    html += f'<h2>{escape_html(L["index_categories"])}</h2>\n'
    for category in sorted(index.keys()):
        html += f"<h3>{escape_html(category.capitalize())}</h3>\n"
        html += "<ul>\n"
        for entry in sorted(index[category]):
            html += f"<li>{entry}</li>\n"
        html += "</ul>\n"
    html += '</div>\n'
    return html


def folio_label(div_id):
    """p003r_1 -> 3r; falls back to the raw id."""
    m = re.match(r'p0*(\d+)([rv])', div_id)
    return f"{m.group(1)}{m.group(2)}" if m else div_id

# entry div id -> ordered list of folios the entry physically spans;
# built by xml_to_html from the per-folio source files in ms-xml/<version>/,
# which are authoritative for which segment sits on which folio
ENTRY_FOLIOS = {}

def folio_key(folio):
    """Sort key for folio labels like '17r' / '17v'."""
    m = re.match(r'0*(\d+)([rv])', folio)
    return (int(m.group(1)), 0 if m.group(2) == 'r' else 1) if m else (9999, 2)

def load_entry_folios(folio_dir):
    """Map each entry id to the folios its segments occupy, in folio order."""
    entry_folios = defaultdict(set)
    for path in sorted(Path(folio_dir).glob('*_p*_preTEI.xml')):
        m = re.search(r'_p0*(\d+[rv])_preTEI', path.name)
        if not m:
            continue
        folio = m.group(1)
        try:
            froot = ET.parse(path).getroot()
        except ET.ParseError as e:
            print(f'Warning: could not parse {path.name}: {e}')
            continue
        for div in froot.iter('div'):
            if div.get('id'):
                entry_folios[div.get('id')].add(folio)
    return {eid: sorted(folios, key=folio_key) for eid, folios in entry_folios.items()}

def folio_range_label(div_id):
    """'17r' for single-folio entries, '17r\u201317v' for spanning ones."""
    folios = ENTRY_FOLIOS.get(div_id)
    if not folios:
        return folio_label(div_id)
    if len(folios) == 1:
        return folios[0]
    return f'{folios[0]}\u2013{folios[-1]}'

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
    html += f'<h2>{escape_html(L["index_tags"])}</h2>\n'
    html += f'<p class="index-note">{escape_html(L["tag_index_note"])}</p>\n'
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

def balance_inline_tags(fragment, context):
    """Close unclosed inline tags so a data typo cannot leak formatting."""
    for tag in ('i', 'b', 'em', 'u', 'sup', 'sub'):
        opens = len(re.findall(f'<{tag}[ >]', fragment))
        closes = len(re.findall(f'</{tag}>', fragment))
        if opens > closes:
            print(f"Warning: unclosed <{tag}> in '{context}' — auto-closing")
            fragment += f'</{tag}>' * (opens - closes)
    return fragment

def load_essay_data(root, csv_file, known_ids=None):
    """
    Loads the essay metadata CSV and returns (by_entry, unlinked):
    by_entry maps entry div ids to lists of essay dicts; unlinked lists essays
    with no (resolvable) entry-id. Malformed but unambiguous entry-ids are
    repaired; unmatched ones produce a build warning. Entry ids are validated
    against the XML root's divs, or against known_ids when no root is given.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Warning: annotation metadata CSV not found at {csv_file}; skipping essay index")
        return {}, []

    if known_ids is None:
        known_ids = {div.get('id') for div in root.iter('div') if div.get('id')}

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
            'title_html': balance_inline_tags(title, f'essay title: {title[:40]}'),
            'authors': row.get('author', '').strip(),
            'url': row.get('edition-URL', '').strip(),
        }
        entry_ids = [e.strip() for e in row.get('entry-id', '').split(';') if e.strip()]
        matched_any = False
        for entry_id in entry_ids:
            normalized = normalize_entry_id(entry_id)
            if normalized:
                by_entry[normalized].append(essay)
                matched_any = True
            else:
                unmatched_ids.add(entry_id)
        # an essay goes to the general group only when it matched no entry at
        # all; a partially-bad id list still lists it under its valid entries
        if not matched_any:
            unlinked.append(essay)
    if unmatched_ids:
        print(f"Warning: essay index: entry-ids not found in XML (listed without links): "
              f"{sorted(unmatched_ids)} — fix in metadata/annotation-metadata.csv")
    return by_entry, unlinked

def create_essay_index_html(root, by_entry, unlinked):
    """
    Creates an index of edition essays grouped by the manuscript entry they
    discuss. Entry headings link to the entry in this document; essay titles
    link to the online edition. Each entry group carries an
    id="essay-entry-<entry_id>" anchor so entry headings in the body can link
    here (see the essay marker in process_element).
    """
    headings = {}
    for div in root.iter('div'):
        div_id = div.get('id')
        head = div.find('head')
        if div_id and head is not None:
            text = re.sub(r'\s+', ' ', ''.join(head.itertext())).strip()
            if text:
                headings[div_id] = text

    def essay_item_html(essay):
        title_html = essay.get('title_html') or escape_html(essay['title'])
        if essay['url']:
            title_html = f'<a href="{escape_html(essay["url"])}">{title_html}</a>'
        authors = f' — {escape_html(essay["authors"])}' if essay['authors'] else ''
        return f'<li>{title_html}{authors}</li>\n'

    html = '<div id="essay-index" class="essay-index" style="page-break-before: always;">\n'
    html += f'<h2>{escape_html(L["index_essays"])}</h2>\n'
    html += f'<p class="index-note">{escape_html(L["essay_index_note"])}</p>\n'
    for entry_id in sorted(by_entry.keys(), key=folio_sort_key):
        heading = headings.get(entry_id, entry_id)
        html += (f'<h4 class="essay-index-entry" id="essay-entry-{escape_html(entry_id)}">'
                 f'<a href="#{escape_html(entry_id)}">'
                 f'{escape_html(heading)} (fol. {escape_html(folio_range_label(entry_id))})</a></h4>\n')
        html += '<ul class="essay-index-essays">\n'
        for essay in sorted(by_entry[entry_id], key=lambda e: e['title']):
            html += essay_item_html(essay)
        html += '</ul>\n'
    if unlinked:
        # dedupe essays that ended up here via multiple unmatched ids
        seen = set()
        unlinked = [e for e in unlinked
                    if not (e['title'] in seen or seen.add(e['title']))]
        html += f'<h4 class="essay-index-entry">{escape_html(L["general_essays"])}</h4>\n'
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

def figure_annotating_comments(ab_elem):
    """Map each comment that directly annotates a figure -> that figure."""
    kids = list(ab_elem)
    return {kids[n]: kids[n - 1] for n in range(1, len(kids))
            if kids[n].tag == 'comment' and kids[n - 1].tag == 'figure'}

def render_ab_children(elem, depth, margin_notes, endnotes, figures, render_semantic):
    """Render an <ab>'s children, binding figure footnote markers to the figure.

    A figure placed out of the text flow (a floated margin figure) would
    otherwise sit on top of the small marker that follows it. Wrapping the
    figure and its marker in one container — and moving any float onto that
    container — keeps the marker beside the image it annotates and visible.
    Endnote numbering is unaffected: markers are generated in document order.
    """
    annotated = figure_annotating_comments(elem)          # comment -> figure
    annotated_figures = set(annotated.values())

    def render(child):
        return process_element(child, depth + 1, margin_notes=margin_notes,
                               endnotes=endnotes, figures=figures,
                               render_semantic=render_semantic)

    parts = []
    pending_figure = None
    for child in elem:
        if child in annotated_figures:
            pending_figure = render(child)
            continue
        rendered = render(child)
        if pending_figure is not None and child in annotated:
            marker, sep, rest = rendered.partition('</sup>')
            fig_html, wrapper_classes = _hoist_placement(pending_figure)
            parts.append(f'<span class="fig-with-note{wrapper_classes}">'
                         f'{fig_html}{marker}{sep}</span>{rest}')
        else:
            if pending_figure is not None:
                parts.append(pending_figure)
            parts.append(rendered)
        pending_figure = None
    if pending_figure is not None:
        parts.append(pending_figure)
    return ''.join(parts)

def _hoist_placement(fig_html):
    """Move a figure's margin float onto its wrapper, so the wrapper floats
    as one unit (image + marker) instead of the image alone."""
    wrapper_classes = ''
    for side in ('left', 'right'):
        token = f' fig-margin fig-margin-{side}'
        if token in fig_html:
            fig_html = fig_html.replace(token, ' fig-margin-inner')
            wrapper_classes = f' fig-margin fig-margin-{side}'
            break
    return fig_html, wrapper_classes

# entry div id -> number of essays; populated by xml_to_html so that
# process_element can mark entries that have essays in the Index of Essays.
# Entries split across folio breaks repeat their div id (the part="y"
# attribute is inconsistently applied), so ESSAY_MARKED tracks ids that have
# already received their marker: exactly one marker per entry, on its first
# segment in document order.
ESSAY_COUNTS = {}
ESSAY_MARKED = set()
RANGE_MARKED = set()
# folio-range label waiting to be placed inside the entry's heading; set by
# the div branch on an entry's first segment, consumed by the head branch
PENDING_FOLIO_RANGE = []

# When True (--figures), figure images are rendered inline in the body at
# their point of reference, sized/positioned from the XML attributes,
# instead of appearing only in the back-of-book List of Figures.
RENDER_FIGURES = False

# child element -> parent; built by xml_to_html so the figure renderer can
# tell mid-text figures (inside <ab>/<head>) from standalone ones
PARENT_MAP = {}

def figure_in_text_flow(elem):
    """True if the figure sits inside running text (<ab> or <head>)."""
    node = PARENT_MAP.get(elem)
    while node is not None:
        if node.tag in ('ab', 'head'):
            return True
        node = PARENT_MAP.get(node)
    return False

def process_element(elem, depth=0, margin_notes=None, endnotes=None, figures=None, render_semantic=False):

    """

    Recursively process XML elements and convert to styled HTML.

    """

    tag = elem.tag

    text = elem.text or ""

    tail = elem.tail or ""

    html = ""



    if tag == "all":

        html = '<div class="manuscript" id="translation">\n'

        for child in elem:

            html += process_element(child, depth + 1, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        html += '</div>\n'

        return html

    elif tag == "div":

        div_id = elem.get("id", "")

        categories = elem.get("categories", "")

        div_margin_notes = []

        html = f'<div class="entry" id="{escape_html(div_id)}" data-categories="{escape_html(categories)}">\n'

        if div_id and div_id not in RANGE_MARKED:

            RANGE_MARKED.add(div_id)

            PENDING_FOLIO_RANGE.clear()

            PENDING_FOLIO_RANGE.append(folio_range_label(div_id))

        essay_count = 0 if div_id in ESSAY_MARKED else ESSAY_COUNTS.get(div_id, 0)

        if essay_count:

            ESSAY_MARKED.add(div_id)

            word = L["essays"] if essay_count > 1 else L["essay"]

            label = f"{essay_count} {word}"

            html += (f'<a class="essay-marker" href="#essay-entry-{escape_html(div_id)}" '
                     f'title="{escape_html(L["see_essays"].format(n=label))}">'
                     f'&#10022;&thinsp;{escape_html(label)}</a>\n')

        if text.strip():

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=div_margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        if PENDING_FOLIO_RANGE:

            html += (f'<span class="folio-range folio-range-floated">fol. '
                     f'{escape_html(PENDING_FOLIO_RANGE.pop())}</span>\n')

        html += '</div>\n'

        if div_margin_notes:

            html += '<div class="margin-notes">\n'

            html += f'<p class="margin-notes-header">{escape_html(L["in_margin"])}</p>\n'

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

        if PENDING_FOLIO_RANGE:

            html += (f' <span class="folio-range">fol. '
                     f'{escape_html(PENDING_FOLIO_RANGE.pop())}</span>')

        html += '</h3>\n'

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "ab":

        margin = elem.get("margin", "")

        render = elem.get("render", "")

        if margin and margin_notes is not None:

            note_html = f'<div class="margin-note" data-position="{escape_html(margin)}">\n'

            note_html += f'<span class="margin-position">[{escape_html(position_label(margin))}]</span> '

            if text:

                note_html += escape_html(text)

            note_html += render_ab_children(elem, depth, None, endnotes, figures, render_semantic)

            note_html += '</div>\n'

            margin_notes.append(note_html)

            return escape_html(tail) if tail else ""

        classes = f"ab {escape_html(margin)} {escape_html(render)}".strip()

        html = f'<p class="{classes}" >'

        if text:

            html += escape_html(text)

        html += render_ab_children(elem, depth, margin_notes, endnotes, figures, render_semantic)

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

        html = f'<span class="ill">{escape_html(L["illegible"])}</span>'

        if text:

            html += escape_html(text)

        for child in elem:

            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)

        if tail:

            html += escape_html(tail)

        return html

    elif tag == "gap":

        return f'<span class="gap">{escape_html(L["gap"])}</span>' + escape_html(tail)

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
                    # Fall back to the figure's Google Drive link (some figures,
                    # e.g. fig_p020r_1, are absent from the edition asset server)
                    drive_id = None
                    link = elem.get("link", "")
                    m_drive = re.search(r'(?:/file/d/|[?&]id=)([\w-]+)', link)
                    if m_drive:
                        drive_id = m_drive.group(1)
                    if drive_id:
                        drive_url = f"https://drive.google.com/uc?export=download&id={drive_id}"
                        try:
                            req = urllib.request.Request(drive_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req) as response:
                                data = response.read()
                            # only keep it if it's actually an image, not a
                            # Drive error/confirmation page
                            if data[:8] == b'\x89PNG\r\n\x1a\n' or data[:3] == b'\xff\xd8\xff':
                                with open(local_img_path, 'wb') as out_file:
                                    out_file.write(data)
                                print(f"Downloaded {drive_url} to {local_img_path} (Drive fallback)")
                            else:
                                print(f"Drive fallback for {fig_id} did not return an image; skipping")
                        except Exception as e2:
                            print(f"Drive fallback for {fig_id} failed: {e2}")

            # Add figure info to the list for later use
            figures.append({
                "id": fig_id,
                "alt_text": alt_text,
                "local_path": local_img_path
            })
            
            if RENDER_FIGURES and local_img_path.exists():
                # Inline image at the point of reference. Size and position
                # are interpreted from the XML attributes:
                #   size:   x-small | small | large | (unset -> default)
                #   margin: manuscript margin placement -> float left/right
                #   render: "tall" -> tighter height cap
                size = elem.get("size", "") or "default"
                margin_attr = elem.get("margin", "")
                # A margin figure never floats: either it is hoisted into the
                # entry's margin-note block (see below), or it is already inside
                # margin content (margin <ab>, which passes margin_notes=None).
                # Floating it would only let it overlay neighbouring text.
                classes = f"fig-inline fig-{size}"
                if not margin_attr and figure_in_text_flow(elem) and size != "large":
                    # figure occurs mid-text with no placement info: keep it
                    # in the line (large figures still break out as blocks)
                    classes += " fig-intext"
                if elem.get("render") == "tall":
                    classes += " fig-tall"
                # inline figures replace the List of Figures, so nothing to link to
                html = (f'<span id="{escape_html(fig_id)}" class="{classes}">'
                        f'<img src="../../images/{escape_html(local_img_path.name)}" '
                        f'alt="{escape_html(alt_text) if alt_text else escape_html(fig_id)}"/>'
                        f'</span>')
            elif RENDER_FIGURES:
                # inline mode, but the image could not be fetched
                html = (f'<span id="{escape_html(fig_id)}" class="figure-missing">'
                        f'{escape_html(L["figure_ref"].format(label=alt_text or fig_id))}</span>')
            else:
                # Create a link to the figure in the list of figures
                html = (f'<a id="{escape_html(fig_id)}" href="#figure-list-{escape_html(fig_id)}">'
                        f'{escape_html(L["figure_ref"].format(label=alt_text or fig_id))}</a>')
        else:
            # Fallback for when figures are not being processed
            html = f'<div class="figure" id="{escape_html(fig_id)}" >'
            html += (f'<p class="figure-placeholder">'
                     f'{escape_html(L["figure_ref"].format(label=alt_text or fig_id))}</p>')

        if text:
            html += escape_html(text)
        for child in elem:
            html += process_element(child, depth + 1, margin_notes=margin_notes, endnotes=endnotes, figures=figures, render_semantic=render_semantic)
        
        if figures is None:
            html += '</div>\n'

        # A margin figure outside margin content becomes its own margin note,
        # keeping it out of the running text (margin <ab> content passes
        # margin_notes=None, so figures already in a margin note stay put).
        margin_attr = elem.get("margin", "")
        if margin_attr and margin_notes is not None:
            note = f'<div class="margin-note" data-position="{escape_html(margin_attr)}">\n'
            note += f'<span class="margin-position">[{escape_html(position_label(margin_attr))}]</span> '
            note += html
            note += '</div>\n'
            margin_notes.append(note)
            return escape_html(tail) if tail else ""

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
    /* Bundled symbol-fallback font: the manuscript uses apothecary/alchemical
       signs the standard fonts lack; without an explicit fallback, fontconfig
       substitutes hidden macOS faces that Acrobat cannot extract. */
    @font-face {
        font-family: "DejaVu Sans";
        src: url("../../lib/fonts/DejaVuSans.ttf");
    }
    @font-face {
        font-family: "DejaVu Sans";
        font-weight: bold;
        src: url("../../lib/fonts/DejaVuSans-Bold.ttf");
    }
    @font-face {
        font-family: "Noto Sans Symbols";
        src: url("../../lib/fonts/NotoSansSymbols-Regular.ttf");
    }

    @page {
        size: letter;
        margin: 1in;
    }

    /* PDF outline bookmarks. The title page and the body's repeated title
       are suppressed; the body title anchors the "Translation" bookmark that
       entry headings nest under. */
    h1 {
        bookmark-level: 1;
        bookmark-label: content();
    }
    .title-page h1,
    .title-page h2 {
        bookmark-level: none;
    }
    h1.doc-title {
        bookmark-level: 1;
        bookmark-label: "__TEXT_SECTION__";
    }
    h3.endnotes-header {
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
    /* Inline figures (--figures mode) */
    .fig-inline {
        display: block;
        text-align: center;
        margin: 8pt auto;
        break-inside: avoid;
    }
    .fig-inline img {
        max-height: 7.5in;
        max-width: 100%;
    }
    .fig-inline.fig-x-small img { max-width: 1.4in; }
    .fig-inline.fig-small img { max-width: 2.4in; }
    .fig-inline.fig-default img { max-width: 3.5in; }
    .fig-inline.fig-large img { max-width: 100%; }
    .fig-inline.fig-tall img { max-height: 5in; }
    .figure-missing {
        font-style: italic;
        color: #777;
    }

    .fig-inline.fig-intext {
        display: inline-block;
        vertical-align: middle;
        margin: 0 3pt;
    }
    .fig-inline.fig-intext.fig-x-small img { max-height: 0.75in; max-width: 1.8in; }
    .fig-inline.fig-intext.fig-small img { max-height: 1.25in; max-width: 2.5in; }
    .fig-inline.fig-intext.fig-default img { max-height: 1.25in; max-width: 2.5in; }
    .fig-inline.fig-margin {
        display: block;
        max-width: 2.4in;
    }
    /* A margin figure must never paint outside its float box: text wraps
       around the box, so an image wider than it would cover that text.
       Size caps live on the <img>, so clamp the image to the box and cap
       box-width per size (unset size would otherwise give a 3.5in image). */
    .fig-inline.fig-margin img {
        max-width: 100%;
    }
    .fig-inline.fig-margin.fig-x-small {
        max-width: 1.4in;
    }
    .fig-inline.fig-margin.fig-default,
    .fig-inline.fig-margin.fig-large {
        max-width: 2.4in;
    }
    .fig-inline.fig-margin-right {
        float: right;
        clear: right;
        margin: 2pt 0 6pt 10pt;
    }
    .fig-inline.fig-margin-left {
        float: left;
        clear: left;
        margin: 2pt 10pt 6pt 0;
    }

    .folio-range {
        font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif;
        font-size: 9pt;
        font-weight: normal;
        color: #792421;
        margin-left: 6pt;
    }
    .folio-range-floated {
        float: right;
        clear: right;
        font-size: 8pt;
        color: #555;
        margin: 2pt 0 2pt 6pt;
    }

    a.essay-marker {
        float: right;
        font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif;
        font-size: 8pt;
        color: #792421;
        text-decoration: none;
        border: 0.5pt solid #79242180;
        border-radius: 3pt;
        padding: 1pt 4pt;
        margin: 2pt 0 2pt 6pt;
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
        font-family: "Garamond", "Georgia", "Times New Roman", "DejaVu Sans", "Noto Sans Symbols", serif;
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

    /* Transcription (source-text) elements */
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

    /* <mark> is a symbol in the source text rendered as a utf-8 character
       (e.g. / - +), not emphasis: it carries no styling of its own. */

    .comment-ref {
        color: #3498db;
        font-size: 0.7em;
        /* never let an out-of-flow neighbour paint over a footnote marker */
        position: relative;
        z-index: 2;
        background-color: #ffffff;
        padding: 0 0.5pt;
    }

    /* a figure and the footnote marker that annotates it travel as one box */
    .fig-with-note {
        display: inline-block;
        vertical-align: middle;
        break-inside: avoid;
    }
    .fig-with-note > .fig-inline,
    .fig-with-note > .figure-missing {
        float: none;
        display: inline-block;
        vertical-align: middle;
        margin: 0;
    }
    .fig-with-note > .comment-ref {
        margin-left: 2pt;
    }
    .fig-with-note.fig-margin-left {
        float: left;
        clear: left;
        margin: 2pt 10pt 6pt 0;
    }
    .fig-with-note.fig-margin-right {
        float: right;
        clear: right;
        margin: 2pt 0 6pt 10pt;
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
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 0.04em;
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
        font-weight: bold;
        color: #16a085;
    }

    .pl {
        font-weight: bold;
        color: #2980b9;
    }

    .pro {
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 0.04em;
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
        font-weight: bold;
    }
    """

    if render_semantic:
        css = base_css + semantic_css
    else:
        css = base_css
    return css.replace('__TEXT_SECTION__', L['text_section'])

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
def xml_to_html(xml_file, output_html, render_semantic=False, render_figures=False, version='tl'):
    global RENDER_FIGURES
    RENDER_FIGURES = render_figures
    print(f"Parsing XML file: {xml_file}")
    csv_file = Path("../metadata/DCE_comment-tracking-Tracking.csv")
    comments_dict = load_comments(csv_file)
    Path("../images").mkdir(exist_ok=True)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    PARENT_MAP.clear()
    PARENT_MAP.update({child: p for p in root.iter() for child in p})
    endnotes = []
    figures = []
    essays_by_entry, essays_unlinked = load_essay_data(root, Path("../metadata/annotation-metadata.csv"))
    ESSAY_COUNTS.clear()
    ESSAY_COUNTS.update({eid: len(essays) for eid, essays in essays_by_entry.items()})
    ESSAY_MARKED.clear()
    RANGE_MARKED.clear()
    ENTRY_FOLIOS.clear()
    ENTRY_FOLIOS.update(load_entry_folios(f'../ms-xml/{version}'))
    spanning = sum(1 for f in ENTRY_FOLIOS.values() if len(f) > 1)
    print(f'Folio extents: {len(ENTRY_FOLIOS)} entries, {spanning} spanning multiple folios')
    print("Converting XML to HTML...")
    body_html = process_element(root, endnotes=endnotes, figures=figures, render_semantic=render_semantic)
    index_html = create_index_html(root)
    tag_index_html = create_tag_index_html(root)
    essay_index_html = create_essay_index_html(root, essays_by_entry, essays_unlinked)
    title_page_html = create_title_page_html()
    toc_html = create_toc_html(include_figure_list=not render_figures)
    # inline figures render in the body, so the back-of-book list is redundant
    figure_list_html = '' if render_figures else create_figure_list_html(figures)
    endnotes_html = ""
    if endnotes:
        print(f"Generating {len(endnotes)} endnotes...")
        endnotes_html = '<div class="endnotes" id="endnotes">\n'
        endnotes_html += f'<h3 class="endnotes-header">{escape_html(L["endnotes"])}</h3>\n'
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
<html lang="{LANG}">
<head>
    <meta charset="UTF-8">
    <title>BnF Ms. Fr. 640 &mdash; {L["text_section"]}</title>
    <style>
    {get_css(render_semantic=render_semantic)}
    </style>
</head>
<body>
    {title_page_html}
    {toc_html}
    <h1 class="doc-title">Secrets of Craft and Nature in Renaissance France</h1>
    <h3>{L["subtitle"]}</h3>
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

def post_process_pdf_links(pdf_file):
    """
    Rewrite internal links from named destinations to explicit destinations
    and normalize link rectangles. WeasyPrint emits links as string /Dest
    names resolved through the document name tree; some viewers (Adobe
    Acrobat in particular) have proven unreliable with that form, while
    explicit [page /XYZ x y z] destinations work everywhere.
    """
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import ArrayObject, FloatObject, NameObject
    except ImportError:
        print("Warning: pypdf not installed; skipping link post-processing.")
        print("Internal links may not work in Adobe Acrobat. pip install pypdf")
        return

    print("Post-processing PDF links (named -> explicit destinations)...")
    reader = PdfReader(pdf_file)

    # name -> raw destination array from the name tree
    root = reader.trailer['/Root']
    name_map = {}
    dests_tree = root.get('/Names', {}).get_object().get('/Dests')
    if dests_tree is None:
        print("No named destinations found; nothing to do.")
        return
    def collect(node):
        node = node.get_object()
        if '/Names' in node:
            arr = node['/Names']
            for i in range(0, len(arr), 2):
                name_map[str(arr[i])] = arr[i + 1]
        for kid in node.get('/Kids', []):
            collect(kid)
    collect(dests_tree)

    rewritten = unresolved = 0
    for page in reader.pages:
        for a in (page.get('/Annots') or []):
            o = a.get_object()
            if o.get('/Subtype') != '/Link':
                continue
            # normalize /Rect to lower-left / upper-right order
            x0, y0, x1, y1 = [float(v) for v in o['/Rect']]
            o[NameObject('/Rect')] = ArrayObject([FloatObject(min(x0, x1)), FloatObject(min(y0, y1)),
                                      FloatObject(max(x0, x1)), FloatObject(max(y0, y1))])
            dest = o.get('/Dest')
            if dest is None or isinstance(dest.get_object(), ArrayObject):
                continue
            target = name_map.get(str(dest))
            if target is not None:
                o[NameObject('/Dest')] = target.get_object()
                rewritten += 1
            else:
                unresolved += 1

    writer = PdfWriter()
    writer.append(reader)
    with open(pdf_file, 'wb') as f:
        writer.write(f)
    print(f"Rewrote {rewritten} internal links to explicit destinations"
          + (f" ({unresolved} unresolved names left as-is)" if unresolved else ""))

def html_to_pdf(html_file, output_pdf):
    try:
        from weasyprint import HTML
        print(f"Generating PDF from HTML: {html_file}")
        HTML(filename=html_file).write_pdf(output_pdf)
        print(f"PDF generated successfully: {output_pdf}")
        post_process_pdf_links(output_pdf)
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
        '--version',
        choices=sorted(VERSION_LANG),
        default='tl',
        help="Manuscript version to render: tl (English translation), tc (diplomatic "
             "French transcription), tcn (normalized French transcription). Generated "
             "apparatus — title page, table of contents, index headings — is written in "
             "the language of the version. Default: tl."
    )
    parser.add_argument(
        '--semantic',
        action='store_true',
        help='If set, render semantic XML elements with special styling (colors, etc.). Default is off.'
    )
    parser.add_argument(
        '--figures',
        action='store_true',
        help='If set, render figure images inline in the body at their point of reference, '
             'sized/positioned from the XML size/margin attributes, and omit the '
             'back-of-book List of Figures. Default is off (figures appear only in '
             'the List of Figures).'
    )
    args = parser.parse_args()

    # Define input and output file paths; each rendering variant gets its own
    # output files so they can coexist (e.g. all_tl_semantic_figures.pdf)
    set_language(args.version)
    v = args.version
    xml_file = Path(f"../allFolios/xml/{v}/all_{v}.xml")
    suffix = ("_semantic" if args.semantic else "") + ("_figures" if args.figures else "")
    html_file = Path(f"../allFolios/pdf/all_{v}{suffix}.html")
    pdf_file = Path(f"../allFolios/pdf/all_{v}{suffix}.pdf")

    # Check if XML file exists
    if not xml_file.exists():
        print(f"ERROR: XML file not found: {xml_file}")
        sys.exit(1)

    # Convert XML to HTML, passing the rendering flags
    xml_to_html(xml_file, html_file, render_semantic=args.semantic,
                render_figures=args.figures, version=args.version)

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