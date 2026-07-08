#!/usr/bin/env python3
"""Step 1 — programmatic print-production checks over the whole document."""
import sys
from collections import Counter, defaultdict

from pypdf import PdfReader

PDF = sys.argv[1] if len(sys.argv) > 1 else 'allFolios/pdf/all_tl_figures.pdf'
reader = PdfReader(PDF)
npages = len(reader.pages)

# ---------------------------------------------------------------- fonts
fonts = {}          # basefont -> dict(subtype, embedded, pages)
for i, page in enumerate(reader.pages):
    res = page.get('/Resources')
    if not res:
        continue
    fd = res.get_object().get('/Font')
    if not fd:
        continue
    for key in fd.get_object():
        f = fd.get_object()[key].get_object()
        base = str(f.get('/BaseFont', '?'))
        sub = str(f.get('/Subtype', '?'))
        # descendant fonts (Type0) carry the descriptor
        desc_holder = f
        if sub == '/Type0' and '/DescendantFonts' in f:
            desc_holder = f['/DescendantFonts'][0].get_object()
        descr = desc_holder.get('/FontDescriptor')
        embedded = False
        if descr is not None:
            d = descr.get_object()
            embedded = any(k in d for k in ('/FontFile', '/FontFile2', '/FontFile3'))
        rec = fonts.setdefault(base, {'subtype': sub, 'embedded': embedded, 'pages': set()})
        rec['pages'].add(i + 1)
        rec['embedded'] = rec['embedded'] or embedded

print('=' * 78)
print(f'FONT INVENTORY — {PDF} ({npages} pages)')
print('=' * 78)
for base in sorted(fonts):
    r = fonts[base]
    name = base.split('+')[-1]
    subset = '+' in base
    print(f'  {name:<34} {r["subtype"]:<10} embedded={str(r["embedded"]):<5} '
          f'subset={str(subset):<5} pages={len(r["pages"])}')
not_embedded = [b for b, r in fonts.items() if not r['embedded']]
print(f'\n  NOT EMBEDDED: {not_embedded or "none"}')

# ---------------------------------------------------------------- geometry
boxes = Counter()
rotations = Counter()
for page in reader.pages:
    mb = page.mediabox
    boxes[(round(float(mb.width), 2), round(float(mb.height), 2))] += 1
    rotations[page.get('/Rotate', 0)] += 1
    for b in ('/CropBox', '/BleedBox', '/TrimBox', '/ArtBox'):
        if b in page:
            boxes[(b, tuple(round(float(v), 2) for v in page[b]))] += 1

print('\n' + '=' * 78)
print('PAGE GEOMETRY')
print('=' * 78)
for k, v in boxes.items():
    print(f'  {k}: {v} pages')
print(f'  rotations: {dict(rotations)}')
print('  (612 x 792 pt = 8.5 x 11 in US Letter)')
print('  TrimBox/BleedBox present:', any(isinstance(k[0], str) for k in boxes))
