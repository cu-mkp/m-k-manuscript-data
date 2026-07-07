#!/usr/bin/env python3
"""
BnF Ms. Fr. 640 Entry Metadata PDF Generator
============================================

Renders metadata/entry_metadata.csv as a PDF reference of the manuscript's
entries: one block per entry, in manuscript order, showing the entry heading
(translation, with the original transcription beneath), folio, categories,
and the entry's tagged terms grouped by semantic tag type (deduplicated,
with occurrence counts). Entry headings link to the entry's folio in the
online edition.

Follows lib/generate_glossary_pdf.py as the model and reuses the pipeline
from lib/generate_pdf_gemini.py.

Run from lib/:  python generate_entry_metadata_pdf.py
Output:         ../metadata/entry-metadata.{html,pdf} (alongside the source CSV)
"""

import csv
import sys
from collections import Counter
from pathlib import Path

from generate_pdf_gemini import (
    TAG_INDEX_TYPES,
    escape_html,
    folio_sort_key,
    html_to_pdf,
    load_essay_data,
)

EDITION_FOLIO_URL = 'https://edition640.makingandknowing.org/#/folios/{folio}/f/{folio}/tl'


def load_entries(csv_file):
    with open(csv_file, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if (r.get('div_id') or '').strip()]
    rows.sort(key=lambda r: folio_sort_key(r['div_id']))
    return rows


def terms_html(row):
    """Tagged terms by semantic type: deduped TL terms with occurrence counts."""
    sections = []
    for tag_type, label in sorted(TAG_INDEX_TYPES.items(), key=lambda kv: kv[1]):
        raw = (row.get(f'{tag_type}_tl') or '').strip()
        if not raw:
            continue
        counts = Counter()
        order = []
        for term in raw.split(';'):
            term = ' '.join(term.split())
            if not term:
                continue
            if term not in counts:
                order.append(term)
            counts[term] += 1
        if not order:
            continue
        rendered = ', '.join(
            escape_html(t) + (f' (&times;{counts[t]})' if counts[t] > 1 else '')
            for t in order
        )
        sections.append(f'<p class="terms"><span class="tag-type">{escape_html(label)}:</span> {rendered}</p>\n')
    return ''.join(sections)


def essays_html(div_id, essays_by_entry):
    essays = essays_by_entry.get(div_id)
    if not essays:
        return ''
    rendered = '; '.join(
        (f'<a href="{escape_html(e["url"])}">{e.get("title_html") or escape_html(e["title"])}</a>'
         if e['url'] else (e.get('title_html') or escape_html(e['title'])))
        + (f' ({escape_html(e["authors"])})' if e['authors'] else '')
        for e in sorted(essays, key=lambda e: e['title'])
    )
    return f'<p class="essays"><span class="tag-type">Essays:</span> {rendered}</p>\n'


def entry_html(row, essays_by_entry):
    div_id = row['div_id'].strip()
    folio = (row.get('folio_display') or row.get('folio') or '').strip()
    heading_tl = ' '.join((row.get('heading_tl') or '').split()) or '[no heading]'
    heading_tc = ' '.join((row.get('heading_tc') or '').split())
    categories = (row.get('categories') or '').strip()

    url = EDITION_FOLIO_URL.format(folio=escape_html(folio)) if folio else None
    heading = escape_html(heading_tl)
    if url:
        heading = f'<a href="{url}">{heading}</a>'

    html = f'<div class="entry-block" id="{escape_html(div_id)}">\n'
    html += (f'<h2 class="entry-heading">{heading} '
             f'<span class="entry-ref">{escape_html(folio)} &middot; {escape_html(div_id)}</span></h2>\n')
    if heading_tc and heading_tc != heading_tl:
        html += f'<p class="heading-tc">{escape_html(heading_tc)}</p>\n'
    if categories:
        html += f'<p class="categories">{escape_html(categories)}</p>\n'
    html += essays_html(div_id, essays_by_entry)
    html += terms_html(row)
    html += '</div>\n'
    return html


def build_html(rows, essays_by_entry):
    body = ''.join(entry_html(r, essays_by_entry) for r in rows)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Entry Metadata - BnF Ms. Fr. 640</title>
<style>
@font-face {{
    font-family: "DejaVu Sans";
    src: url("../lib/fonts/DejaVuSans.ttf");
}}
@font-face {{
    font-family: "DejaVu Sans";
    font-weight: bold;
    src: url("../lib/fonts/DejaVuSans-Bold.ttf");
}}
@page {{ size: letter; margin: 1in; }}
body {{ font-family: "Garamond", "Georgia", "Times New Roman", "DejaVu Sans", serif; font-size: 10pt; line-height: 1.4; }}
h1 {{ bookmark-level: 1; bookmark-label: content(); font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif; }}
.title-page {{ text-align: center; margin-top: 2.5in; page-break-after: always; }}
.title-page h1 {{ font-size: 24pt; margin-bottom: 0.3em; }}
.title-page h2 {{ font-size: 14pt; font-weight: normal; bookmark-level: none; }}
.title-page .note {{ font-size: 9pt; color: #444; margin-top: 2em; text-align: left; }}
.entry-block {{ margin-bottom: 12pt; break-inside: avoid; }}
h2.entry-heading {{
    bookmark-level: 2; bookmark-label: content();
    font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif;
    font-size: 11pt; margin: 0 0 2pt 0;
    border-bottom: 0.5pt solid #d1d1d1; padding-bottom: 2pt;
}}
.entry-ref {{ font-weight: normal; font-size: 9pt; color: #792421; }}
p.heading-tc {{ font-style: italic; color: #555; margin: 0 0 2pt 0; }}
p.categories {{ margin: 0 0 2pt 0; text-transform: uppercase; letter-spacing: 0.08em; font-size: 8pt; color: #555; }}
p.terms {{ margin: 0 0 1pt 1.5em; text-indent: -1.5em; font-size: 9pt; }}
p.essays {{ margin: 0 0 1pt 1.5em; text-indent: -1.5em; font-size: 9pt; }}
p.essays a {{ color: #792421; }}
.tag-type {{ font-family: "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif; font-size: 8pt; color: #792421; }}
a {{ color: inherit; text-decoration: none; }}
h2.entry-heading a {{ color: #792421; }}
</style>
</head>
<body>
<div class="title-page">
    <h1>Entry Metadata</h1>
    <h2>Secrets of Craft and Nature in Renaissance France<br/>
        A Digital Critical Edition and English Translation of BnF Ms. Fr. 640</h2>
    <p class="note">One block per manuscript entry, in manuscript order: the entry heading
        (English translation, linked to the entry&rsquo;s folio in the online edition) with the
        original French transcription beneath, the entry&rsquo;s categories, its associated
        research essays (linked to the online edition), and its tagged terms
        grouped by semantic tag type &mdash; deduplicated, with occurrence counts &mdash; from the
        translation. Source: metadata/entry_metadata.csv.</p>
</div>
{body}
</body>
</html>
"""


def main():
    csv_file = Path('../metadata/entry_metadata.csv')
    html_file = Path('../metadata/entry-metadata.html')
    pdf_file = Path('../metadata/entry-metadata.pdf')

    if not csv_file.exists():
        print(f'ERROR: entry metadata CSV not found: {csv_file}')
        sys.exit(1)

    rows = load_entries(csv_file)
    print(f'Loaded {len(rows)} entries')

    known_ids = {r['div_id'].strip() for r in rows}
    essays_by_entry, _ = load_essay_data(
        None, Path('../metadata/annotation-metadata.csv'), known_ids=known_ids)
    print(f'{len(essays_by_entry)} entries have associated essays')

    html_file.write_text(build_html(rows, essays_by_entry), encoding='utf-8')
    print(f'Wrote {html_file}')

    if html_to_pdf(str(html_file), str(pdf_file)):
        print(f'\n✓ Entry metadata PDF complete: {pdf_file}')
    else:
        print(f'\n✓ HTML complete: {html_file} (install weasyprint for PDF)')


if __name__ == '__main__':
    main()
