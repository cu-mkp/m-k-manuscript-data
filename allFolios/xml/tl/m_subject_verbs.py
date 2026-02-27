#!/usr/bin/env python3
"""
NLP analysis of Ms. de Houleur XML (tl/all_tl.xml).

For every semantic tag type, find transitive action verbs where the
tagged entity is the grammatical subject of a clause, together with
the direct object of each such verb.

Usage
-----
    ~/nlp-venv/bin/python m_subject_verbs.py

Outputs
-------
    subject_verb_obj_detail.csv   – one row per (subject, verb, object) triple
    subject_verb_obj_summary.csv  – grouped by (tag, term, verb) with objects
    caveats.md                    – methodology notes and known limitations
"""

import re
import csv
import sys
from collections import defaultdict
from datetime import date
from lxml import etree
import spacy

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

XML_FILE        = "/Users/thc4/Github/m-k-manuscript-data/allFolios/xml/tl/all_tl.xml"
OUTPUT_DETAIL   = "subject_verb_obj_detail.csv"
OUTPUT_SUMMARY  = "subject_verb_obj_summary.csv"
OUTPUT_CAVEATS  = "caveats.md"
SPACY_MODEL     = "en_core_web_sm"

# All semantic entity tags tracked as potential grammatical subjects.
# Language tags (fr, la, it, …) and editorial markup (add, corr, exp, …)
# are intentionally excluded — see caveats report for rationale.
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
SUBJECT_TAGS = frozenset(TAG_LABELS)

# Tags whose entire content (text + descendants) is dropped from NLP text.
SKIP_TAGS = frozenset({
    'comment', 'del', 'figure', 'gap', 'hr', 'ill', 'mark',
})

# Tags replaced by a single space.
SPACE_TAGS = frozenset({'lb'})

# Copular / stative verbs excluded as non-action.
COPULA_LEMMAS = frozenset({
    'be', 'seem', 'appear', 'become', 'remain', 'look', 'feel', 'sound',
})

# Priority order for nested tag resolution: tags earlier in this list
# beat tags later when a token falls inside multiple spans.
# <m> has absolute priority; all other tags resolve by tightest span.
M_PRIORITY_TAG = 'm'


# ---------------------------------------------------------------------------
# XML text extraction
# ---------------------------------------------------------------------------

def extract_text_and_subject_spans(element):
    """
    Walk *element*, building a plain-text string and recording the
    character-level positions of every element in SUBJECT_TAGS.

    Each span carries its originating tag name.  Nested spans are each
    recorded independently; overlap is resolved later by
    tightest_subject_span().

    Returns
    -------
    (raw_text : str, raw_spans : list of (start, end, text, tag))
    """
    buf   = []
    spans = []
    pos   = [0]

    def walk(node):
        tag = node.tag if isinstance(node.tag, str) else None
        if tag is None:
            return
        if tag in SKIP_TAGS:
            return
        if tag in SPACE_TAGS:
            buf.append(' ');  pos[0] += 1
            return

        is_subject = tag in SUBJECT_TAGS
        if is_subject:
            s_start = pos[0]
            s_tag   = tag

        if node.text:
            buf.append(node.text);  pos[0] += len(node.text)

        for child in node:
            walk(child)
            if child.tail:
                buf.append(child.tail);  pos[0] += len(child.tail)

        if is_subject:
            s_end  = pos[0]
            s_text = ''.join(buf)[s_start:s_end]
            spans.append((s_start, s_end, s_text.strip(), s_tag))

    walk(element)
    return ''.join(buf), spans


def normalise_and_remap_spans(raw_text, raw_spans):
    """
    Collapse whitespace runs to single spaces and re-locate each span
    by searching for its (normalised) text in document order.

    Returns (norm_text, norm_spans) where each span is (start, end, text, tag).
    """
    norm_text = re.sub(r'\s+', ' ', raw_text).strip()
    norm_spans = []
    search_from = 0

    for (_, _, raw_span_text, tag) in raw_spans:
        s_norm = re.sub(r'\s+', ' ', raw_span_text).strip()
        if not s_norm:
            continue
        idx = norm_text.find(s_norm, search_from)
        if idx == -1:
            idx = norm_text.find(s_norm)   # fallback to start
        if idx == -1:
            continue
        end = idx + len(s_norm)
        norm_spans.append((idx, end, s_norm, tag))
        search_from = end

    return norm_text, norm_spans


# ---------------------------------------------------------------------------
# Span-lookup helpers
# ---------------------------------------------------------------------------

def tightest_subject_span(token, spans):
    """
    Return (term_text, tag) of the best span containing *token*, or None.

    Priority rules
    --------------
    1. <m> always beats any other tag — a plant/tool/etc. inside a
       material tag is still reported as the material.
    2. Among non-<m> tags, the tightest (shortest) span wins.
    3. Ties within the same tag type are broken by shortest span.
    """
    t_start  = token.idx
    t_end    = t_start + len(token.text)
    best_m   = None          # (length, text)
    best_other = None        # (length, text, tag)

    for (ms, me, mt, tag) in spans:
        if t_start >= ms and t_end <= me:
            length = me - ms
            if tag == M_PRIORITY_TAG:
                if best_m is None or length < best_m[0]:
                    best_m = (length, mt)
            else:
                if best_other is None or length < best_other[0]:
                    best_other = (length, mt, tag)

    if best_m is not None:
        return (best_m[1], M_PRIORITY_TAG)
    if best_other is not None:
        return (best_other[1], best_other[2])
    return None


def noun_chunk_for(token, doc):
    """Full noun-chunk text for *token*, or the token text if no chunk found."""
    for chunk in doc.noun_chunks:
        if chunk.root == token:
            return chunk.text
    return token.text


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    print(f"Loading spaCy model '{SPACY_MODEL}' …", flush=True)
    nlp = spacy.load(SPACY_MODEL)

    print(f"Parsing {XML_FILE} …", flush=True)
    tree = etree.parse(XML_FILE)
    root = tree.getroot()

    results  = []
    all_abs  = list(root.iter('ab'))
    total    = len(all_abs)
    ab_count = 0   # paragraphs that had at least one tagged span
    print(f"Processing {total:,} <ab> elements …", flush=True)

    for i, ab in enumerate(all_abs):
        if i % 500 == 0 and i > 0:
            print(f"  {i:,}/{total:,} …", flush=True)

        # Walk up to the enclosing <div> for its id
        div_id = ''
        node = ab.getparent()
        while node is not None:
            if isinstance(node.tag, str) and node.tag == 'div':
                div_id = node.get('id', '')
                break
            node = node.getparent()

        # Also grab div categories if present
        div_node = ab.getparent()
        categories = ''
        while div_node is not None:
            if isinstance(div_node.tag, str) and div_node.tag == 'div':
                categories = div_node.get('categories', '')
                break
            div_node = div_node.getparent()

        raw_text, raw_spans = extract_text_and_subject_spans(ab)
        if not raw_text.strip() or not raw_spans:
            continue

        text, spans = normalise_and_remap_spans(raw_text, raw_spans)
        if not text or not spans:
            continue

        ab_count += 1
        doc = nlp(text)

        for token in doc:
            if token.dep_ not in ('nsubj', 'nsubjpass'):
                continue

            match = tightest_subject_span(token, spans)
            if match is None:
                continue
            subject_term, subject_tag = match

            verb = token.head
            if verb.pos_ not in ('VERB', 'AUX'):
                continue
            verb_lemma = verb.lemma_
            if verb_lemma in COPULA_LEMMAS:
                continue

            obj_tokens = [c for c in verb.children if c.dep_ in ('obj', 'dobj')]
            if not obj_tokens:
                continue

            # 300-char window around the subject token, clipped to the <ab> block.
            # Avoids both spaCy's over-eager sentence segmentation and
            # the risk of very long <ab> blocks flooding the output.
            window    = 300
            ctx_start = max(0, token.idx - window)
            ctx_end   = min(len(text), token.idx + len(token.text) + window)
            sentence  = text[ctx_start:ctx_end].strip()
            is_passive = token.dep_ == 'nsubjpass'

            for obj_tok in obj_tokens:
                if obj_tok.pos_ == 'PRON':
                    continue
                obj_text    = noun_chunk_for(obj_tok, doc)
                obj_match   = tightest_subject_span(obj_tok, spans)
                obj_tag     = obj_match[1] if obj_match else ''
                results.append({
                    'div_id':       div_id,
                    'categories':   categories,
                    'subject_tag':  subject_tag,
                    'subject_label': TAG_LABELS.get(subject_tag, subject_tag),
                    'subject_term': subject_term,
                    'verb_lemma':   verb_lemma,
                    'verb_form':    verb.text,
                    'passive':      is_passive,
                    'obj_text':     obj_text,
                    'obj_tag':      obj_tag,
                    'sentence':     sentence,
                })

    print(f"\nFound {len(results):,} triples across {ab_count:,} paragraphs.",
          flush=True)

    # -----------------------------------------------------------------------
    # Detail CSV
    # -----------------------------------------------------------------------
    print(f"Writing {OUTPUT_DETAIL} …")
    with open(OUTPUT_DETAIL, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'div_id', 'categories', 'subject_tag', 'subject_label',
            'subject_term', 'verb_lemma', 'verb_form', 'passive',
            'obj_text', 'obj_tag', 'sentence',
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    # -----------------------------------------------------------------------
    # Summary CSV — grouped by (subject_tag, subject_term, verb_lemma)
    # -----------------------------------------------------------------------
    print(f"Writing {OUTPUT_SUMMARY} …")
    counts: dict = defaultdict(lambda: defaultdict(int))
    for r in results:
        key = (r['subject_tag'], r['subject_label'], r['subject_term'], r['verb_lemma'])
        counts[key][r['obj_text']] += 1

    with open(OUTPUT_SUMMARY, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['subject_tag', 'subject_label', 'subject_term',
                    'verb_lemma', 'total_count', 'objects'])
        # Sort by label then term then verb
        for key in sorted(counts, key=lambda x: (x[1].lower(), x[2].lower(), x[3])):
            tag, label, term, verb = key
            obj_counts = counts[key]
            total = sum(obj_counts.values())
            obj_list = '; '.join(
                f"{o} ({n})" if n > 1 else o
                for o, n in sorted(obj_counts.items(), key=lambda x: (-x[1], x[0]))
            )
            w.writerow([tag, label, term, verb, total, obj_list])

    # -----------------------------------------------------------------------
    # Per-tag counts for the caveats report
    # -----------------------------------------------------------------------
    tag_counts: dict = defaultdict(int)
    for r in results:
        tag_counts[r['subject_tag']] += 1

    passive_count = sum(1 for r in results if r['passive'])

    write_caveats(tag_counts, passive_count, ab_count, len(results))
    print("Done.")


# ---------------------------------------------------------------------------
# Caveats report
# ---------------------------------------------------------------------------

def write_caveats(tag_counts, passive_count, ab_count, total_triples):
    print(f"Writing {OUTPUT_CAVEATS} …")

    # Build tag result table
    tag_rows = []
    for tag in sorted(TAG_LABELS, key=lambda t: TAG_LABELS[t]):
        n = tag_counts.get(tag, 0)
        tag_rows.append(f"| `<{tag}>` | {TAG_LABELS[tag]} | {n} |")

    tag_table = '\n'.join(tag_rows)

    report = f"""\
# NLP Analysis — Caveats and Methodology Notes

**Date:** {date.today().isoformat()}
**Script:** `m_subject_verbs.py`
**Model:** spaCy `en_core_web_sm`
**Source:** `all_tl.xml` (English translation layer)

---

## What the analysis does

For each semantic tag type in the manuscript XML, the script identifies
sentences where the tagged entity is the **grammatical subject** of a
**transitive verb**, and records the **direct object** of that verb.
This yields triples of the form **(subject entity) — VERB → (object)**.

**Summary of run:**
- `<ab>` blocks processed: {ab_count:,} (of {ab_count:,} that contained at least one tracked tag)
- Triples found: {total_triples:,}
- Passive-voice triples: {passive_count:,} ({passive_count/total_triples*100:.1f}%)

**Results per tag type:**

| Tag | Label | Triples |
|-----|-------|---------|
{tag_table}

---

## Caveats

### 1. NLP model accuracy

The model (`en_core_web_sm`) is a small statistical parser trained on
modern English (news, web text, OntoNotes). The manuscript is a
16th-century craftsman's notebook with archaic syntax, contractions,
technical vocabulary, and hybrid French-English constructions.
Dependency parse accuracy on this material will be **lower** than the
~90% the model achieves on modern text benchmarks. Errors tend to cluster
around:

- Long, comma-heavy sentences common in recipe text
- Gerund and infinitive subjects ("Beating X with Y loosens…")
- Sentences beginning with an imperative followed by a dependent clause
- Archaic word order ("put in it two ounces of…")

Results should be treated as a **first-pass signal**, not a ground truth.
The `sentence` column in the detail CSV allows manual verification of
every triple.

### 2. Multi-word tagged spans — head token only

spaCy's dependency parser assigns the `nsubj` arc to a **single head
token** within a noun phrase. For a span like `<m>turpentine oil</m>`,
the head is typically `oil`; for `<tl>copper vessel</tl>` it is
`vessel`. Only that head token's character position is checked against
tagged spans. If the head token is also a standalone tag elsewhere in
the same paragraph (e.g., `oil` appears both inside `<m>turpentine
oil</m>` and as bare `<m>oil</m>`), the span-remapping algorithm
searches in document order and should assign the correct instance, but
misattribution is possible in dense passages.

### 3. Pronoun objects excluded

Direct objects that are pronouns (`it`, `them`, `themselves`, etc.) are
dropped. Resolving pronouns to their referents requires **coreference
resolution**, which `en_core_web_sm` does not support. A future pass
with a model that includes coref (e.g., the `coreferee` extension or a
transformer-based model) could recover these.

### 4. Passive constructions included

Both active (`nsubj`) and passive (`nsubjpass`) subjects are captured.
In passive sentences the grammatical subject is the **patient** — the
entity acted upon — not the agent. The `passive` column (True/False) in
the detail CSV flags these rows. Example:

> *eau-de-vie is also **made** well* → subject: `eau-de-vie`, verb: `make`

Here `eau-de-vie` is what gets made, not who makes it. These are
semantically useful (they describe what happens to the material) but
structurally different from active transitive uses.

### 5. Coordinated subjects

In sentences like *"Sulfur and vermilion makes the same effect"*, spaCy
marks one conjunct as `nsubj` and the other as `conj`. Only the `nsubj`
token is checked for span membership, so **one conjunct may be missed**.
The missed conjunct is still visible in the `sentence` column.

### 6. Copular and stative verbs excluded

The following verb lemmas are excluded as non-action:
`be`, `seem`, `appear`, `become`, `remain`, `look`, `feel`, `sound`.

Existential statements (*"X is a substance"*) and stative descriptions
(*"X seems fragile"*) are absent from the results. Add lemmas to
`COPULA_LEMMAS` in the script to adjust.

### 7. Only direct objects captured

The analysis captures **syntactic direct objects** (`obj` / `dobj`) only.
The following object types are **not** captured:

| Construction | Example | Dep label |
|---|---|---|
| Prepositional object | *acts **on** the mold* | `pobj` |
| Clausal complement | *causes **it to melt*** | `xcomp` / `ccomp` |
| Secondary predicate | *renders **it flexible*** | `oprd` / `xcomp` |
| Indirect object | *gives **the craftsman** color* | `iobj` / `dative` |

### 8. Non-English text

The manuscript contains passages tagged `<fr>`, `<la>`, `<it>`, `<de>`,
`<es>`, `<el>`, `<oc>`, `<po>`. These are **not** excluded from the NLP
text (removing them could corrupt sentence structure), but the English
model will parse them incorrectly. Named entities in `<pn>` and `<pl>`
spans are often French or Latinate and may also parse poorly.

### 9. Excluded XML content

The following XML elements are **stripped from the text** before NLP
processing:

| Tag | Reason |
|-----|--------|
| `<del>` | Struck-through text — author crossed it out |
| `<ill>` | Illegible text in source |
| `<gap>` | Lacuna in source |
| `<comment>` | Editorial note reference (empty element) |
| `<figure>` | Graphical object |
| `<hr>` | Horizontal rule |
| `<mark>` | Manuscript symbols (e.g. `|`, `/`) |

`<lb>` (line break) is replaced with a space.

### 10. Nested tag priority

When multiple tracked tags overlap, the following rules apply:

1. `<m>` (Material) has **absolute priority** over all other tags. A
   plant (`<pa>`), tool (`<tl>`), etc. nested inside `<m>` is reported
   under the `<m>` term.
2. Among all other tag types, the **tightest** (innermost / shortest)
   span wins.

### 11. Unit of analysis

Each `<ab>` (anonymous block) is processed independently. Sentences
that span an `<ab>` boundary (possible in `continued="yes"` entries)
are split and each half parsed separately, which may degrade parse
quality at boundaries.

### 12. Sparse tag types

Several tag types rarely or never appear as grammatical subjects in
recipe/craft prose. Tags with zero or very few results (e.g., `<cn>`,
`<ms>`, `<mu>`, `<tmp>`) are expected — these entity types typically
appear as objects, adjuncts, or modifiers rather than agents of action.

---

## Column reference

### `subject_verb_obj_detail.csv`

| Column | Description |
|--------|-------------|
| `div_id` | `id` attribute of the enclosing `<div>` |
| `categories` | `categories` attribute of the enclosing `<div>` |
| `subject_tag` | XML tag name of the subject entity |
| `subject_label` | Human-readable label for the tag |
| `subject_term` | Full text of the tagged span |
| `verb_lemma` | Lemmatised verb |
| `verb_form` | Inflected verb form as it appears in text |
| `passive` | True if the subject is a passive (`nsubjpass`) |
| `obj_text` | Full noun-chunk text of the direct object |
| `obj_tag` | XML tag of the object (if tagged), else empty |
| `sentence` | Full sentence for verification |

### `subject_verb_obj_summary.csv`

One row per unique `(subject_tag, subject_term, verb_lemma)` group, with
all attested objects listed in the `objects` column (frequency in
parentheses if > 1).
"""

    with open(OUTPUT_CAVEATS, 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()
