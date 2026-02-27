#!/usr/bin/env python3
"""Build ms_fr_640_nlp.ipynb using nbformat to guarantee valid JSON."""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

COLAB_BADGE = (
    "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
    "(https://colab.research.google.com/github/cu-mkp/m-k-manuscript-data/blob/"
    "nlp-analysis/allFolios/xml/tl/ms_fr_640_nlp.ipynb)\n\n"
)

cells = []

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell(COLAB_BADGE + """\
# Who Does What to What? Entity-Role Extraction in Ms. Fr. 640

This notebook applies dependency-based NLP to the English translation of
[BnF Ms. Fr. 640](https://edition640.makingandknowing.org/), a 16th-century
French craftsman's manuscript digitised and encoded by the
[Making and Knowing Project](https://www.makingandknowing.org/) (Columbia University).

**Research question:** For each semantic entity type tagged in the XML
(materials, tools, animals, professions, ...), what *transitive action verbs*
appear when that entity is the grammatical subject of a clause -- and what
are the direct objects of those verbs?

**Method in brief:**
1. Parse the XML, extracting plain text while tracking the character positions of every semantic tag.
2. Run spaCy dependency parsing sentence by sentence.
3. For every nominal subject (`nsubj` / `nsubjpass`) whose position falls inside a tagged span, record the head verb and its direct object.
4. Filter: transitive verbs only, no copulas, no pronoun objects.

> **Read the Caveats section** at the bottom before drawing conclusions.
> This is an exploratory, first-pass analysis using a small general-purpose model."""))

# ---------------------------------------------------------------------------
# 1. Setup
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("## 1 · Setup\nInstall dependencies and download the spaCy English model. Run once per session."))

cells.append(new_code_cell("""\
%%capture
!pip install spacy lxml wordcloud matplotlib
!python -m spacy download en_core_web_sm"""))

cells.append(new_code_cell("""\
import re
import math
import urllib.request
from collections import defaultdict

import spacy
from lxml import etree
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from wordcloud import WordCloud

print('All imports OK')"""))

# ---------------------------------------------------------------------------
# 2. Load XML
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 2 · Load the manuscript XML

Fetched directly from the public Making and Knowing GitHub repository -- no upload required."""))

cells.append(new_code_cell("""\
XML_URL  = "https://raw.githubusercontent.com/cu-mkp/m-k-manuscript-data/master/allFolios/xml/tl/all_tl.xml"
XML_FILE = "all_tl.xml"

urllib.request.urlretrieve(XML_URL, XML_FILE)
print(f"Downloaded {XML_FILE}")"""))

# ---------------------------------------------------------------------------
# 3. Configuration
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 3 · Configuration

### Semantic tag vocabulary

The manuscript XML uses a controlled tag vocabulary developed by the Making and Knowing Project.
We track all 17 semantic tags as potential grammatical subjects.
Language tags (`<fr>`, `<la>`, ...) and editorial markup (`<add>`, `<del>`, ...) are excluded -- see Caveats."""))

cells.append(new_code_cell("""\
TAG_LABELS = {
    'al':  'Animal',
    'bp':  'Body Part',
    'cn':  'Currency',
    'df':  'Definition',
    'env': 'Environment',
    'm':   'Material',
    'md':  'Medical Term',
    'ms':  'Measurement',
    'mu':  'Musical Instrument',
    'pa':  'Plant',
    'pl':  'Place',
    'pn':  'Personal Name',
    'pro': 'Profession',
    'sn':  'Sense Term',
    'tl':  'Tool',
    'tmp': 'Temporal',
    'wp':  'Weapon',
}
SUBJECT_TAGS  = frozenset(TAG_LABELS)
SKIP_TAGS     = frozenset({'comment', 'del', 'figure', 'gap', 'hr', 'ill', 'mark'})
SPACE_TAGS    = frozenset({'lb'})
COPULA_LEMMAS = frozenset({'be', 'seem', 'appear', 'become', 'remain', 'look', 'feel', 'sound'})
M_PRIORITY_TAG = 'm'

print(f"{len(TAG_LABELS)} semantic tags tracked")"""))

# ---------------------------------------------------------------------------
# 4. Extraction functions
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 4 · XML text extraction

For each `<ab>` (anonymous text block), we walk the element tree and build:
- a plain-text string suitable for NLP
- a list of `(start, end, text, tag)` spans marking where each semantic tag appears

Character positions are tracked incrementally so multi-word spans are handled correctly."""))

cells.append(new_code_cell("""\
def extract_text_and_subject_spans(element):
    buf, spans, pos = [], [], [0]

    def walk(node):
        tag = node.tag if isinstance(node.tag, str) else None
        if tag is None: return
        if tag in SKIP_TAGS: return
        if tag in SPACE_TAGS:
            buf.append(' '); pos[0] += 1; return

        is_subj = tag in SUBJECT_TAGS
        if is_subj:
            s_start, s_tag = pos[0], tag
        if node.text:
            buf.append(node.text); pos[0] += len(node.text)
        for child in node:
            walk(child)
            if child.tail:
                buf.append(child.tail); pos[0] += len(child.tail)
        if is_subj:
            s_text = ''.join(buf)[s_start:pos[0]]
            spans.append((s_start, pos[0], s_text.strip(), s_tag))

    walk(element)
    return ''.join(buf), spans


def normalise_and_remap_spans(raw_text, raw_spans):
    norm = re.sub(r'\\s+', ' ', raw_text).strip()
    out, search_from = [], 0
    for (_, _, raw_t, tag) in raw_spans:
        s = re.sub(r'\\s+', ' ', raw_t).strip()
        if not s: continue
        idx = norm.find(s, search_from)
        if idx == -1: idx = norm.find(s)
        if idx == -1: continue
        end = idx + len(s)
        out.append((idx, end, s, tag))
        search_from = end
    return norm, out


print('Extraction functions defined')"""))

# ---------------------------------------------------------------------------
# 5. Analysis
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 5 · NLP analysis

For every sentence in every `<ab>` block:
1. Find tokens with dependency relation `nsubj` or `nsubjpass`.
2. Check whether the token's character position falls inside a tagged span.
3. If the head verb is transitive (has a direct object child), record the triple.

When tags are nested, `<m>` (Material) takes priority; otherwise the tightest span wins."""))

cells.append(new_code_cell("""\
def tightest_subject_span(token, spans):
    t0, t1 = token.idx, token.idx + len(token.text)
    best_m, best_oth = None, None
    for (ms, me, mt, tag) in spans:
        if t0 >= ms and t1 <= me:
            length = me - ms
            if tag == M_PRIORITY_TAG:
                if best_m is None or length < best_m[0]: best_m = (length, mt)
            else:
                if best_oth is None or length < best_oth[0]: best_oth = (length, mt, tag)
    if best_m   is not None: return (best_m[1], M_PRIORITY_TAG)
    if best_oth is not None: return (best_oth[1], best_oth[2])
    return None


def noun_chunk_for(token, doc):
    for chunk in doc.noun_chunks:
        if chunk.root == token: return chunk.text
    return token.text


print('Analysis functions defined')"""))

cells.append(new_code_cell("""\
print("Loading spaCy model ...")
nlp = spacy.load('en_core_web_sm')

print("Parsing XML ...")
root = etree.parse(XML_FILE).getroot()

rows = []
all_abs = list(root.iter('ab'))
print(f"Processing {len(all_abs):,} <ab> blocks ...")

for i, ab in enumerate(all_abs):
    if i % 500 == 0 and i > 0:
        print(f"  {i:,} / {len(all_abs):,}")

    div_id = categories = ''
    node = ab.getparent()
    while node is not None:
        if isinstance(node.tag, str) and node.tag == 'div':
            div_id     = node.get('id', '')
            categories = node.get('categories', '')
            break
        node = node.getparent()

    raw_text, raw_spans = extract_text_and_subject_spans(ab)
    if not raw_text.strip() or not raw_spans: continue

    text, spans = normalise_and_remap_spans(raw_text, raw_spans)
    if not text or not spans: continue

    doc = nlp(text)
    for token in doc:
        if token.dep_ not in ('nsubj', 'nsubjpass'): continue
        match = tightest_subject_span(token, spans)
        if match is None: continue
        subject_term, subject_tag = match

        verb = token.head
        if verb.pos_ not in ('VERB', 'AUX'): continue
        if verb.lemma_ in COPULA_LEMMAS: continue

        obj_tokens = [c for c in verb.children if c.dep_ in ('obj', 'dobj')]
        if not obj_tokens: continue

        window     = 300
        ctx_start  = max(0, token.idx - window)
        ctx_end    = min(len(text), token.idx + len(token.text) + window)
        sentence   = text[ctx_start:ctx_end].strip()
        is_passive = token.dep_ == 'nsubjpass'
        for obj_tok in obj_tokens:
            if obj_tok.pos_ == 'PRON': continue
            obj_text  = noun_chunk_for(obj_tok, doc)
            obj_match = tightest_subject_span(obj_tok, spans)
            rows.append({
                'div_id':        div_id,
                'categories':    categories,
                'subject_tag':   subject_tag,
                'subject_label': TAG_LABELS.get(subject_tag, subject_tag),
                'subject_term':  subject_term,
                'verb_lemma':    verb.lemma_,
                'verb_form':     verb.text,
                'passive':       is_passive,
                'obj_text':      obj_text,
                'obj_tag':       obj_match[1] if obj_match else '',
                'sentence':      sentence,
            })

df = pd.DataFrame(rows)
print(f"\\nFound {len(df):,} subject-verb-object triples")"""))

# ---------------------------------------------------------------------------
# 6. Results
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("## 6 · Results\n\n### 6.1 · Triples per entity type"))

cells.append(new_code_cell("""\
tag_summary = (
    df.groupby(['subject_tag', 'subject_label'])
      .size()
      .reset_index(name='triples')
      .sort_values('triples', ascending=False)
)
tag_summary"""))

cells.append(new_markdown_cell("""\
### 6.2 · Browse by entity type

Change `TAG` to any tag abbreviation (`m`, `tl`, `pro`, `al`, `wp`, `pl`, ...)."""))

cells.append(new_code_cell("""\
TAG = 'm'   # <- change this

view = (
    df[df.subject_tag == TAG]
      [['subject_term', 'verb_lemma', 'obj_text', 'passive', 'div_id', 'sentence']]
      .sort_values(['verb_lemma', 'subject_term'])
      .reset_index(drop=True)
)
print(f"{len(view)} triples for <{TAG}> ({TAG_LABELS.get(TAG, TAG)})")
view"""))

cells.append(new_markdown_cell("### 6.3 · Aggregated summary -- top verb-object pairs per entity type"))

cells.append(new_code_cell("""\
summary = (
    df.groupby(['subject_label', 'subject_term', 'verb_lemma', 'obj_text'])
      .size()
      .reset_index(name='count')
      .sort_values(['subject_label', 'count'], ascending=[True, False])
      .reset_index(drop=True)
)
summary[summary['count'] > 1]"""))

cells.append(new_markdown_cell("### 6.4 · Verbs of desire / necessity\n\nWhich entities express need, want, or requirement?"))

cells.append(new_code_cell("""\
desire_verbs = ['want', 'need', 'require', 'demand', 'wish']
df[df.verb_lemma.isin(desire_verbs)][['subject_label', 'subject_term', 'verb_lemma', 'obj_text', 'sentence']]"""))

# ---------------------------------------------------------------------------
# 7. Word clouds
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 7 · Word clouds

One cloud per entity type. Word size reflects verb frequency --
how often entities of that type perform that kind of action."""))

cells.append(new_code_cell("""\
TAG_COLORS = {
    'Material':'#1f77b4', 'Profession':'#d62728', 'Tool':'#2ca02c',
    'Weapon':'#ff7f0e', 'Place':'#9467bd', 'Measurement':'#8c564b',
    'Animal':'#e377c2', 'Sense Term':'#7f7f7f', 'Personal Name':'#bcbd22',
    'Plant':'#17becf', 'Environment':'#aec7e8', 'Temporal':'#ffbb78',
    'Definition':'#98df8a',
}

def make_colormap(hex_color):
    r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    def color_func(word, font_size, position, orientation, random_state=None, **kw):
        f = 0.55 + random_state.uniform(0, 0.35)
        return (int(r*f), int(g*f), int(b*f))
    return color_func

freq_by_label = (
    df.groupby(['subject_label', 'verb_lemma'])
      .size().reset_index(name='n')
)
labels_with_data = [
    lbl for lbl in freq_by_label.subject_label.unique()
    if freq_by_label[freq_by_label.subject_label == lbl].verb_lemma.nunique() >= 2
]

n, ncols = len(labels_with_data), 2
nrows = math.ceil(n / ncols)
fig = plt.figure(figsize=(18, 5 * nrows))
fig.suptitle(
    "Transitive verb clouds by entity type\\n(word size proportional to frequency)",
    fontsize=15, fontweight='bold', y=1.01
)
gs = gridspec.GridSpec(nrows, ncols, figure=fig, hspace=0.45, wspace=0.1)

for idx, label in enumerate(sorted(labels_with_data)):
    subset    = freq_by_label[freq_by_label.subject_label == label]
    freq_dict = dict(zip(subset.verb_lemma, subset.n))
    tag       = df[df.subject_label == label].subject_tag.iloc[0]
    wc = WordCloud(
        width=800, height=380, background_color='white',
        max_words=80, prefer_horizontal=0.85,
        color_func=make_colormap(TAG_COLORS.get(label, '#555555')),
        collocations=False, min_font_size=10,
    ).generate_from_frequencies(freq_dict)
    row, col = divmod(idx, ncols)
    ax = fig.add_subplot(gs[row, col])
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f"{label}  <{tag}>  ({sum(freq_dict.values())} triples)", fontsize=12, fontweight='bold')

for idx in range(n, nrows * ncols):
    row, col = divmod(idx, ncols)
    fig.add_subplot(gs[row, col]).axis('off')

plt.show()"""))

# ---------------------------------------------------------------------------
# 8. Export
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("## 8 · Export results"))

cells.append(new_code_cell("""\
df.to_csv('subject_verb_obj_detail.csv', index=False)

summary_out = (
    df.groupby(['subject_tag', 'subject_label', 'subject_term', 'verb_lemma'])
      .agg(
          total_count=('obj_text', 'count'),
          objects=('obj_text', lambda x: '; '.join(
              f"{v} ({k})" if k > 1 else v
              for v, k in sorted(pd.Series(x).value_counts().items(), key=lambda t: -t[1])
          ))
      )
      .reset_index()
      .sort_values(['subject_label', 'subject_term', 'verb_lemma'])
)
summary_out.to_csv('subject_verb_obj_summary.csv', index=False)

print('Saved CSVs. Use File -> Download in the Colab sidebar to save them locally.')"""))

# ---------------------------------------------------------------------------
# 9. Caveats
# ---------------------------------------------------------------------------
cells.append(new_markdown_cell("""\
---

## 9 · Caveats and methodology notes

### Model accuracy
`en_core_web_sm` is a small statistical model trained on modern English (news, web text).
Ms. Fr. 640 is 16th-century craftsman's prose with archaic syntax, technical vocabulary,
and mixed French-English constructions. Parse accuracy is lower than the ~90% on standard benchmarks.
The `sentence` column lets you verify every triple manually.

### What is and isn't captured

| Included | Excluded |
|---|---|
| Active subjects (`nsubj`) | Copulas: *be, seem, appear, become, remain* |
| Passive subjects (`nsubjpass`) -- flagged in `passive` column | Pronoun objects (*it, them, itself*) -- need coreference resolution |
| Direct objects (`obj` / `dobj`) | Prepositional objects (*acts on X*, *works with X*) |
| All 17 semantic tag types | Language tags (`<fr>`, `<la>`, ...) -- not tracked as subjects |

### Multi-word spans
spaCy assigns `nsubj` to a single head token. For `<m>turpentine oil</m>`,
the head is typically `oil`. Only that token's character position is checked against spans.

### Coordinated subjects
In "Sulfur and vermilion makes the same effect", spaCy marks one as `nsubj`
and the other as `conj` -- only the `nsubj` token is matched.

### Nested tags -- priority rules
When a token falls inside overlapping spans: `<m>` wins over all others;
among non-`<m>` tags, the tightest (innermost) span wins.

### Excluded XML content
`<del>` (struck-through), `<ill>` (illegible), `<gap>` (lacuna), `<comment>`,
`<figure>`, `<hr>`, `<mark>` are stripped. `<lb>` (line break) is replaced with a space.

### Sparse tag types
`<bp>`, `<cn>`, `<md>`, `<mu>` returned zero triples -- these entity types
appear primarily as objects or adjuncts in recipe prose, not as agents of action.

---

*Data: [Making and Knowing Project](https://www.makingandknowing.org/), Columbia University.*
*XML encoding: [ms-transcription schema](https://github.com/cu-mkp/m-k-manuscript-data/tree/master/schema).*"""))

# ---------------------------------------------------------------------------
# Write notebook
# ---------------------------------------------------------------------------
nb = new_notebook(cells=cells)
nb['metadata']['colab'] = {'provenance': [], 'toc_visible': True}
nb['metadata']['kernelspec'] = {'display_name': 'Python 3', 'name': 'python3'}

with open('ms_fr_640_nlp.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("ms_fr_640_nlp.ipynb written successfully")
