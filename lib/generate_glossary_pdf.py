#!/usr/bin/env python3
"""
BnF Ms. Fr. 640 Glossary PDF Generator
======================================

Renders metadata/DCE-glossary-table.csv as a PDF, following the entry format
of the online edition's glossary view (making-knowing-edition
src/component/GlossaryView.js and scripts/glossary.js):

    {head-word}, {alternate-spellings} (mod. {modern-spelling}), {pos}:
    1. {meaning} [{references}] 2. ... , see also ->X, syn. ->Y, ant. ->Z

with alphabetic section headers between letter groups. Cross-references that
match another head-word are linked to that entry. Reuses the weasyprint +
pypdf explicit-destination pipeline from generate_pdf_gemini.py.

Run from lib/:  python generate_glossary_pdf.py
Output:         ../allFolios/pdf/glossary.{html,pdf}
"""

import csv
import re
import sys
from pathlib import Path

from generate_pdf_gemini import escape_html, html_to_pdf


def slugify(head_word):
    return 'gloss-' + re.sub(r'[^a-z0-9]+', '-', head_word.casefold()).strip('-')


def load_glossary(csv_file):
    """Group CSV rows into entries by head-word, preserving CSV order.

    Mirrors making-knowing-edition scripts/glossary.js: the first row of a
    head-word supplies spellings and cross-references; every row contributes
    a meaning (part of speech, meaning text, references).
    """
    entries = {}
    with open(csv_file, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            head_word = (row.get('head-word') or '').strip()
            if not head_word:
                continue
            meaning = {
                'partOfSpeech': (row.get('part-of-speech') or '').strip(),
                'meaning': (row.get('meaning') or '').strip(),
                'references': (row.get('references') or '').strip(),
            }
            if head_word in entries:
                entries[head_word]['meanings'].append(meaning)
            else:
                entries[head_word] = {
                    'headWord': head_word,
                    'alternateSpellings': (row.get('alternate-spellings') or '').strip(),
                    'modernSpelling': (row.get('modern-spelling') or '').strip(),
                    'synonym': (row.get('synonym-in-glossary') or '').strip(),
                    'antonym': (row.get('antonym-in-glossary') or '').strip(),
                    'seeAlso': (row.get('see-also-in-glossary') or '').strip(),
                    'meanings': [meaning],
                }
    return entries


def render_meanings(entry):
    """1. meaning [refs] 2. meaning [refs] ... (numbering only when several)."""
    parts = []
    meanings = entry['meanings']
    for i, meaning in enumerate(meanings, 1):
        ref = f' [{escape_html(meaning["references"])}]' if meaning['references'] else ''
        num = f'{i}. ' if len(meanings) > 1 else ''
        # meaning text may contain markup (e.g. <i>) — pass through raw,
        # matching the web view's HTML parsing of these fields
        parts.append(f'{num}{meaning["meaning"]}{ref}')
    return ' '.join(parts)


def xref_html(label, value, known):
    """Render a cross-reference, linking each term that matches a head-word."""
    if not value:
        return ''
    linked = []
    for term in re.split(r',\s*', value):
        target = known.get(term.casefold())
        if target:
            linked.append(f'<a href="#{slugify(target)}">{escape_html(term)}</a>')
        else:
            linked.append(escape_html(term))
    return f'{label} <span class="xref-arrow">&#8594;</span>{", ".join(linked)}'


def entry_html(entry, known):
    head = f'<span class="head-word">{escape_html(entry["headWord"])}</span>'
    alt = f', {escape_html(entry["alternateSpellings"])}' if entry['alternateSpellings'] else ''
    mod = f' (mod. {escape_html(entry["modernSpelling"])})' if entry['modernSpelling'] else ''
    pos = entry['meanings'][0]['partOfSpeech']
    pos_str = f' {escape_html(pos)}:' if pos else ''
    mod_punct = ',' if pos else ':'
    meanings = render_meanings(entry)

    tail_parts = []
    if entry['seeAlso']:
        comma = '' if meanings.rstrip().endswith('.') else ','
        tail_parts.append(f'{comma} see also {xref_html("", entry["seeAlso"], known)}')
    if entry['synonym']:
        tail_parts.append(f', syn. {xref_html("", entry["synonym"], known)}')
    if entry['antonym']:
        tail_parts.append(f', ant. {xref_html("", entry["antonym"], known)}')
    tail = ''.join(tail_parts).replace(' <span class="xref-arrow">', '<span class="xref-arrow">')

    return (f'<p class="gloss-entry" id="{slugify(entry["headWord"])}">'
            f'{head}{alt}{mod}{mod_punct}{pos_str} {meanings}{tail}</p>\n')


def build_html(entries):
    known = {e['headWord'].casefold(): e['headWord'] for e in entries.values()}

    body = ''
    seen_letters = set()
    for entry in entries.values():
        letter = entry['headWord'][0].upper()
        if letter not in seen_letters:
            seen_letters.add(letter)
            body += (f'<h2 class="letter-head" id="letter-{escape_html(letter)}">'
                     f'&mdash; {escape_html(letter)} &mdash;</h2>\n')
        body += entry_html(entry, known)

    letter_links = ' '.join(
        f'<a href="#letter-{escape_html(l)}">{escape_html(l)}</a>'
        for e in [None] for l in sorted(seen_letters)
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Glossary - BnF Ms. Fr. 640</title>
<style>
@page {{ size: letter; margin: 1in; }}
body {{ font-family: "Martel", serif; font-size: 10pt; line-height: 1.45; }}
h1 {{ bookmark-level: 1; bookmark-label: content(); font-family: "Lato", sans-serif; }}
h2.letter-head {{
    bookmark-level: 2; bookmark-label: content();
    font-family: "Lato", sans-serif; text-align: center;
    margin: 1.2em 0 0.6em 0;
}}
.title-page {{ text-align: center; margin-top: 2.5in; page-break-after: always; }}
.title-page h1 {{ font-size: 24pt; margin-bottom: 0.3em; }}
.title-page h2 {{ font-size: 14pt; font-weight: normal; bookmark-level: none; }}
.title-page .cite, .title-page .note {{ font-size: 9pt; color: #444; margin-top: 2em; text-align: left; }}
p.gloss-entry {{
    margin: 0 0 4pt 0;
    padding-left: 1.5em;
    text-indent: -1.5em;
}}
.head-word {{ font-weight: bold; }}
.xref-arrow {{ color: #792421; }}
a {{ color: #792421; text-decoration: none; }}
</style>
</head>
<body>
<div class="title-page">
    <h1>Glossary</h1>
    <h2>Secrets of Craft and Nature in Renaissance France<br/>
        A Digital Critical Edition and English Translation of BnF Ms. Fr. 640</h2>
    <p class="note">For short titles, e.g., [COT1611], see the edition
        <a href="https://edition640.makingandknowing.org/#/content/resources/bibliography">Bibliography</a>.</p>
    <p class="cite">&ldquo;Glossary.&rdquo; In <i>Secrets of Craft and Nature in Renaissance France.
        A Digital Critical Edition and English Translation of BnF Ms. Fr. 640</i>, edited by
        Making and Knowing Project, Pamela H. Smith, Naomi Rosenkranz, Tianna Helena Uchacz,
        Tillmann Taape, Cl&eacute;ment Godbarge, Sophie Pitman, Jenny Boulboull&eacute;, Joel Klein,
        Donna Bilak, Marc Smith, and Terry Catapano. New York: Making and Knowing Project, 2020.
        <a href="https://edition640.makingandknowing.org/#/folios/1r/f/1r/glossary">https://edition640.makingandknowing.org/#/folios/1r/f/1r/glossary</a>.</p>
</div>
<p class="letter-links">{letter_links}</p>
{body}
</body>
</html>
"""


def main():
    csv_file = Path('../metadata/DCE-glossary-table.csv')
    html_file = Path('../allFolios/pdf/glossary.html')
    pdf_file = Path('../allFolios/pdf/glossary.pdf')

    if not csv_file.exists():
        print(f'ERROR: glossary CSV not found: {csv_file}')
        sys.exit(1)

    entries = load_glossary(csv_file)
    print(f'Loaded {len(entries)} glossary entries '
          f'({sum(len(e["meanings"]) for e in entries.values())} meanings)')

    html = build_html(entries)
    html_file.write_text(html, encoding='utf-8')
    print(f'Wrote {html_file}')

    if html_to_pdf(str(html_file), str(pdf_file)):
        print(f'\n✓ Glossary PDF complete: {pdf_file}')
    else:
        print(f'\n✓ HTML complete: {html_file} (install weasyprint for PDF)')


if __name__ == '__main__':
    main()
