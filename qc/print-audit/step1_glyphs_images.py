#!/usr/bin/env python3
"""Step 1b — per-font glyph usage, image PPI, and content overflow."""
import sys
import unicodedata
from collections import Counter, defaultdict

import pdfplumber

PDF = sys.argv[1]
MARGIN_PT = 72.0            # 1in margins per @page rule
PAGE_W, PAGE_H = 612.0, 792.0

font_chars = defaultdict(Counter)   # fontname -> Counter(char)
font_pages = defaultdict(set)
images = []                          # (page, ppi_x, ppi_y, w_px, h_px, w_pt)
overflow = []                        # (page, kind, bbox)

with pdfplumber.open(PDF) as pdf:
    for pno, page in enumerate(pdf.pages, 1):
        for ch in page.chars:
            fn = ch['fontname'].split('+')[-1]
            font_chars[fn][ch['text']] += 1
            font_pages[fn].add(pno)
            # content outside the page box, or past the 1in margin
            if ch['x1'] > PAGE_W or ch['x0'] < 0 or ch['bottom'] > PAGE_H or ch['top'] < 0:
                overflow.append((pno, 'char-off-page', ch['text'], round(ch['x0'],1), round(ch['top'],1)))
            elif ch['x1'] > PAGE_W - MARGIN_PT + 1 or ch['x0'] < MARGIN_PT - 1:
                overflow.append((pno, 'char-past-margin', ch['text'], round(ch['x0'],1), round(ch['x1'],1)))
        for im in page.images:
            w_pt = im['x1'] - im['x0']
            h_pt = im['bottom'] - im['top']
            sw, sh = im.get('srcsize', (0, 0))
            if w_pt > 0 and h_pt > 0 and sw and sh:
                images.append((pno, sw / (w_pt / 72), sh / (h_pt / 72), sw, sh, round(w_pt, 1)))
            if im['x1'] > PAGE_W or im['x0'] < 0 or im['bottom'] > PAGE_H or im['top'] < 0:
                overflow.append((pno, 'image-off-page', '', round(im['x0'],1), round(im['top'],1)))

print('=' * 78)
print('GLYPHS BY FONT  (fallback fonts reveal silent substitution)')
print('=' * 78)
for fn in sorted(font_chars, key=lambda f: -sum(font_chars[f].values())):
    total = sum(font_chars[fn].values())
    sample = font_chars[fn].most_common(12)
    chars = ' '.join(f'{c!r}x{n}' for c, n in sample)
    print(f'\n  {fn}  ({total} glyphs, {len(font_pages[fn])} pages)')
    print(f'    {chars}')
    if fn not in ('Georgia', 'Georgia-Bold', 'Georgia-Italic', 'Georgia-Bold-Italic', 'Helvetica-Neue'):
        uniq = sorted({c for c in font_chars[fn]})
        named = [f'U+{ord(c):04X} {unicodedata.name(c, "?")}' for c in uniq[:25] if c.strip()]
        print('    distinct: ' + '; '.join(named))

print('\n' + '=' * 78)
print(f'RASTER IMAGES — {len(images)} placements')
print('=' * 78)
if images:
    low = [i for i in images if min(i[1], i[2]) < 300]
    print(f'  below 300 PPI: {len(low)} of {len(images)}')
    ppis = sorted(min(i[1], i[2]) for i in images)
    print(f'  min={ppis[0]:.0f}  median={ppis[len(ppis)//2]:.0f}  max={ppis[-1]:.0f} PPI')
    worst = sorted(images, key=lambda i: min(i[1], i[2]))[:12]
    for p, px, py, sw, sh, wpt in worst:
        print(f'    p.{p:<4} {sw}x{sh}px placed {wpt}pt wide -> {min(px,py):.0f} PPI')

print('\n' + '=' * 78)
print(f'CONTENT OVERFLOW — {len(overflow)} occurrences')
print('=' * 78)
kinds = Counter(o[1] for o in overflow)
print('  ', dict(kinds))
pages = sorted({o[0] for o in overflow})
print(f'  pages affected: {len(pages)}  first 20: {pages[:20]}')
for o in overflow[:15]:
    print('   ', o)
