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

# --- Standard library imports -----------------------------------------------
import re                       # regular expressions, used for whitespace cleanup
import csv                      # writing results to CSV files
import sys                      # not used directly but available if needed
from collections import defaultdict  # a dict that auto-creates missing keys
from datetime import date       # used to timestamp the caveats report

# --- Third-party imports -----------------------------------------------------
from lxml import etree          # fast XML parser; reads the manuscript file
import spacy                    # NLP library; handles tokenisation and dependency parsing


# =============================================================================
# CONFIGURATION
# Everything you might want to tweak is gathered here at the top.
# =============================================================================

# Path to the manuscript XML file (the English translation layer)
XML_FILE        = "/Users/thc4/Github/m-k-manuscript-data/allFolios/xml/tl/all_tl.xml"

# Output file names
OUTPUT_DETAIL   = "subject_verb_obj_detail.csv"   # every individual triple found
OUTPUT_SUMMARY  = "subject_verb_obj_summary.csv"  # aggregated by term + verb
OUTPUT_CAVEATS  = "caveats.md"                    # methodology notes

# The spaCy language model to use.
# 'en_core_web_sm' is the small English model — fast but less accurate.
# Switch to 'en_core_web_lg' or 'en_core_web_trf' for better accuracy.
SPACY_MODEL     = "en_core_web_sm"

# ---------------------------------------------------------------------------
# Semantic entity tags we want to treat as potential grammatical subjects.
# Each key is the XML tag name; each value is a human-readable label.
#
# We deliberately exclude:
#   - Language tags (fr, la, it, de, es, el, oc, po): these wrap non-English
#     text that the English NLP model cannot parse reliably.
#   - Editorial markup (add, corr, exp, sup, …): these describe how text was
#     written or corrected, not what kind of entity it is.
# ---------------------------------------------------------------------------
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

# A frozenset (immutable set) of just the tag names, for fast membership tests
SUBJECT_TAGS = frozenset(TAG_LABELS)

# ---------------------------------------------------------------------------
# XML tags whose content is completely removed before NLP processing.
# Including these would introduce noise into the text the NLP model sees.
#
#   comment – editorial note references (empty elements, no text)
#   del     – text the author crossed out; not part of the intended text
#   figure  – graphical objects, no readable text
#   gap     – lacunae (places where text is missing from the manuscript)
#   hr      – horizontal rules (dividers), no text
#   ill     – illegible passages
#   mark    – manuscript symbols like '|' or '/' used as markers
# ---------------------------------------------------------------------------
SKIP_TAGS = frozenset({
    'comment', 'del', 'figure', 'gap', 'hr', 'ill', 'mark',
})

# XML tags replaced by a single space in the extracted text.
# <lb> marks a line break in the manuscript; we treat it as a word separator.
SPACE_TAGS = frozenset({'lb'})

# ---------------------------------------------------------------------------
# Copular (linking) verbs that are excluded from results.
# These verbs connect a subject to a description rather than expressing an
# action, so they do not tell us what the entity *does*.
# Examples: "Colophony IS nothing other than rosin" (identity, not action)
#           "The varnish SEEMS thick" (state, not action)
# ---------------------------------------------------------------------------
COPULA_LEMMAS = frozenset({
    'be', 'seem', 'appear', 'become', 'remain', 'look', 'feel', 'sound',
})

# When a token falls inside more than one tagged span (e.g. <pa> nested
# inside <m>), we need a tiebreaker. <m> (Material) always wins, because
# the manuscript's primary concern is how materials behave.
M_PRIORITY_TAG = 'm'


# =============================================================================
# XML TEXT EXTRACTION
# =============================================================================

def extract_text_and_subject_spans(element):
    """
    Walk a single XML element (typically an <ab> block) and do two things:

    1. Build a plain-text string by concatenating all readable text content,
       skipping or replacing certain tags as configured above.

    2. Record the character positions (start, end) of every element whose
       tag is in SUBJECT_TAGS, along with the element's text and tag name.
       These are called 'spans'.

    Why track character positions?
    --------------------------------
    After extraction, we pass the plain text to spaCy for NLP analysis.
    spaCy returns tokens with character offsets into that plain text.
    By knowing where each tagged span starts and ends in the plain text,
    we can later ask: "is this spaCy token inside a <m> tag?" and answer
    it precisely, even for multi-word tags like <m>turpentine oil</m>.

    How the tree walk works
    -------------------------
    XML elements have two kinds of text:
      - node.text  : text directly inside the opening tag, before any child
      - child.tail : text that follows a child's closing tag, still inside
                     the parent element

    For example: <ab>Take <m>oil</m> and mix</ab>
      ab.text  = "Take "
      m.text   = "oil"
      m.tail   = " and mix"   ← this is the tail of <m>, part of <ab>'s flow

    We process these in order to build the text in reading sequence.

    Returns
    -------
    (raw_text : str, raw_spans : list of (start, end, text, tag))
        'raw' because whitespace has not yet been normalised.
        Positions are character offsets into raw_text.
    """
    buf   = []    # accumulates text fragments; joined at the end
    spans = []    # list of (start, end, text, tag) for each subject element
    pos   = [0]   # running character counter; wrapped in a list so the
                  # nested function 'walk' can modify it (Python closures
                  # cannot reassign variables from the enclosing scope, but
                  # they can mutate mutable objects like lists)

    def walk(node):
        """Recursively process one XML node and all its children."""

        # lxml represents XML comments and processing instructions as nodes
        # with non-string tag values. Skip them.
        tag = node.tag if isinstance(node.tag, str) else None
        if tag is None:
            return

        # If this element is in SKIP_TAGS, ignore it and all its content.
        # Note: the element's 'tail' (text after its closing tag) is added
        # by the *parent's* loop, so we don't lose it here.
        if tag in SKIP_TAGS:
            return

        # If this is a line-break tag, insert a space in the text stream
        # and move on — it has no text content of its own.
        if tag in SPACE_TAGS:
            buf.append(' ')
            pos[0] += 1
            return

        # Check whether this element is one we track as a potential subject.
        is_subject = tag in SUBJECT_TAGS
        if is_subject:
            # Record the position where this tagged span begins
            s_start = pos[0]
            s_tag   = tag

        # Add the element's own text (the part directly after the opening tag)
        if node.text:
            buf.append(node.text)
            pos[0] += len(node.text)

        # Recurse into each child element, then add the child's tail text
        for child in node:
            walk(child)
            # child.tail is the text between this child's closing tag and
            # the next sibling's opening tag — it belongs to the current
            # element's text flow, so we add it here after walking the child.
            if child.tail:
                buf.append(child.tail)
                pos[0] += len(child.tail)

        # If this was a tracked element, record where it ends
        if is_subject:
            s_end  = pos[0]
            # Slice the accumulated buffer to get the exact span text
            s_text = ''.join(buf)[s_start:s_end]
            spans.append((s_start, s_end, s_text.strip(), s_tag))

    walk(element)
    return ''.join(buf), spans


def normalise_and_remap_spans(raw_text, raw_spans):
    """
    The raw text extracted from XML may have irregular whitespace —
    multiple spaces, newlines, tabs — because XML formatting does not
    always reflect the intended reading text. This function:

    1. Collapses any run of whitespace into a single space and strips
       leading/trailing whitespace. This is what we feed to spaCy.

    2. Re-locates each span in the normalised text by searching for its
       (also normalised) text string. We search in document order —
       advancing our search position after each match — so that if the
       same word appears multiple times, we match the right occurrence.

    Why re-locate rather than adjust offsets mathematically?
    ---------------------------------------------------------
    Calculating exactly how whitespace compression shifts each character
    position is fiddly and error-prone. Searching for the span text is
    simpler and reliable for all but pathological edge cases (e.g. the
    exact same multi-word phrase appearing twice in the same block).

    Returns
    -------
    (norm_text : str, norm_spans : list of (start, end, text, tag))
    """
    # Collapse whitespace to single spaces
    norm_text = re.sub(r'\s+', ' ', raw_text).strip()

    norm_spans  = []
    search_from = 0   # keeps track of where to start the next search,
                      # so we match spans in left-to-right document order

    for (_, _, raw_span_text, tag) in raw_spans:
        # Normalise the span text in the same way as the full text
        s_norm = re.sub(r'\s+', ' ', raw_span_text).strip()
        if not s_norm:
            continue   # skip any span that became empty after normalisation

        # Search for this span text starting from the last match position
        idx = norm_text.find(s_norm, search_from)

        # Fallback: if not found from current position (can happen when
        # whitespace normalisation reorders spans), try from the beginning
        if idx == -1:
            idx = norm_text.find(s_norm)

        if idx == -1:
            continue   # span text not found at all — skip it

        end = idx + len(s_norm)
        norm_spans.append((idx, end, s_norm, tag))

        # Advance the search position so the next span is found after this one
        search_from = end

    return norm_text, norm_spans


# =============================================================================
# SPAN-LOOKUP HELPERS
# =============================================================================

def tightest_subject_span(token, spans):
    """
    Given a spaCy token and a list of tagged spans, return the text and
    tag of the *best* span that contains this token, or None if no span
    contains it.

    "Best" is defined by two priority rules:

    Rule 1 — <m> wins unconditionally
        If any <m> (Material) span contains the token, we return that,
        regardless of any other spans. This handles cases like:
            <m><pa>marshmallow</pa> root</m>
        where 'marshmallow' is inside both a <pa> and an <m>. We want
        to report it as a Material subject, not a Plant subject.

    Rule 2 — tightest span wins among non-<m> tags
        If multiple non-<m> spans contain the token, the shortest one
        wins (innermost/most specific). If lengths are equal, the first
        one in the list wins.

    Parameters
    ----------
    token : spaCy Token
        The token to look up (typically a subject token from the parser).
    spans : list of (start, end, text, tag)
        The tagged spans for the current <ab> block.

    Returns
    -------
    (term_text, tag) if a containing span is found, else None.
    """
    # Character range of the token within the normalised text
    t_start = token.idx
    t_end   = t_start + len(token.text)

    best_m     = None   # best <m> span found: (length, text)
    best_other = None   # best non-<m> span found: (length, text, tag)

    for (ms, me, mt, tag) in spans:
        # Check whether the token falls entirely within this span.
        # (t_start >= ms) means the token starts at or after the span start.
        # (t_end <= me)   means the token ends at or before the span end.
        if t_start >= ms and t_end <= me:
            length = me - ms   # span length in characters

            if tag == M_PRIORITY_TAG:
                # Keep the shortest <m> span (most specific)
                if best_m is None or length < best_m[0]:
                    best_m = (length, mt)
            else:
                # Keep the shortest non-<m> span
                if best_other is None or length < best_other[0]:
                    best_other = (length, mt, tag)

    # Return the best <m> span if one was found; otherwise the best other span
    if best_m is not None:
        return (best_m[1], M_PRIORITY_TAG)
    if best_other is not None:
        return (best_other[1], best_other[2])
    return None


def noun_chunk_for(token, doc):
    """
    Return the full noun-phrase text for a given token.

    spaCy identifies 'noun chunks' — base noun phrases like
    'the colored water' or 'a fine sheen'. The head of such a chunk
    is its main noun. If our object token is the head of a noun chunk,
    we return the whole chunk rather than just the single word, giving
    more informative output.

    Falls back to the token's own text if no chunk is found.

    Parameters
    ----------
    token : spaCy Token  — the direct-object head token
    doc   : spaCy Doc    — the parsed document (needed to iterate chunks)
    """
    for chunk in doc.noun_chunks:
        if chunk.root == token:
            return chunk.text
    return token.text


# =============================================================================
# MAIN ANALYSIS LOOP
# =============================================================================

def main():

    # -------------------------------------------------------------------------
    # Step 1: Load the NLP model
    # -------------------------------------------------------------------------
    # spacy.load() reads the model from disk and builds a processing pipeline.
    # For 'en_core_web_sm' this pipeline includes:
    #   - tokeniser  : splits text into tokens (words, punctuation, etc.)
    #   - tagger     : assigns part-of-speech tags (NOUN, VERB, ADJ, …)
    #   - parser     : builds a dependency tree linking tokens to each other
    #   - ner        : named entity recognition (not used here)
    print(f"Loading spaCy model '{SPACY_MODEL}' …", flush=True)
    nlp = spacy.load(SPACY_MODEL)

    # -------------------------------------------------------------------------
    # Step 2: Parse the XML file
    # -------------------------------------------------------------------------
    # etree.parse() reads the XML and builds an element tree in memory.
    # getroot() returns the top-level element of the tree.
    print(f"Parsing {XML_FILE} …", flush=True)
    tree = etree.parse(XML_FILE)
    root = tree.getroot()

    results  = []               # will hold one dict per triple found
    all_abs  = list(root.iter('ab'))  # collect every <ab> element in the document
    total    = len(all_abs)
    ab_count = 0                # counts <ab> blocks that contained tagged spans
    print(f"Processing {total:,} <ab> elements …", flush=True)

    # -------------------------------------------------------------------------
    # Step 3: Process each <ab> block
    # -------------------------------------------------------------------------
    # <ab> (anonymous block) is the manuscript's basic paragraph unit.
    # Each recipe, instruction, or note lives in one or more <ab> elements.
    for i, ab in enumerate(all_abs):

        # Print progress every 500 blocks so the user knows it's still running
        if i % 500 == 0 and i > 0:
            print(f"  {i:,}/{total:,} …", flush=True)

        # --- Find the enclosing <div> and read its attributes ---------------
        # Each <ab> sits inside a <div> which has an 'id' (e.g. "p003r_2")
        # and often a 'categories' attribute (e.g. "varnish;painting").
        # We walk up the tree from the <ab> until we find a <div> parent.
        div_id = ''
        node = ab.getparent()
        while node is not None:
            if isinstance(node.tag, str) and node.tag == 'div':
                div_id = node.get('id', '')
                break
            node = node.getparent()

        categories = ''
        div_node = ab.getparent()
        while div_node is not None:
            if isinstance(div_node.tag, str) and div_node.tag == 'div':
                categories = div_node.get('categories', '')
                break
            div_node = div_node.getparent()

        # --- Extract text and span positions from the XML -------------------
        raw_text, raw_spans = extract_text_and_subject_spans(ab)

        # Skip this block if it has no text or no tracked tagged spans
        if not raw_text.strip() or not raw_spans:
            continue

        # --- Normalise whitespace and re-locate spans -----------------------
        text, spans = normalise_and_remap_spans(raw_text, raw_spans)
        if not text or not spans:
            continue

        ab_count += 1

        # --- Run the NLP pipeline on the cleaned text -----------------------
        # nlp(text) tokenises the text and runs the full pipeline, returning
        # a Doc object. The Doc contains tokens, each with:
        #   token.text    : the surface form (e.g. "resists")
        #   token.lemma_  : the dictionary form (e.g. "resist")
        #   token.pos_    : coarse part-of-speech (e.g. "VERB")
        #   token.dep_    : dependency relation to its head (e.g. "nsubj")
        #   token.head    : the token this one depends on
        #   token.idx     : character offset in the text string
        doc = nlp(text)

        # --- Search every token for subject-verb-object triples -------------
        for token in doc:

            # We only care about nominal subjects:
            #   nsubj    : subject of an active verb ("oil resists water")
            #   nsubjpass: subject of a passive verb ("oil is applied")
            if token.dep_ not in ('nsubj', 'nsubjpass'):
                continue

            # Check whether this subject token falls inside a tracked span
            match = tightest_subject_span(token, spans)
            if match is None:
                continue   # token is not inside any tagged entity span

            subject_term, subject_tag = match

            # --- Get the verb -----------------------------------------------
            # In a dependency tree, the subject token's 'head' is the verb
            # it depends on. For "oil resists water", 'oil' depends on 'resists'.
            verb = token.head

            # We only want actual verbs (VERB) or auxiliaries acting as main
            # verbs (AUX). This filters out cases where spaCy mistakenly
            # assigns a noun or adjective as the subject's head.
            if verb.pos_ not in ('VERB', 'AUX'):
                continue

            # Get the dictionary form of the verb (lemma) for grouping.
            # e.g. "resists", "resisted", "resist" all map to lemma "resist"
            verb_lemma = verb.lemma_

            # Exclude copular verbs — they describe state, not action
            if verb_lemma in COPULA_LEMMAS:
                continue

            # --- Find the direct object(s) ----------------------------------
            # In the dependency tree, direct objects are children of the verb
            # with dependency label 'obj' (spaCy v3) or 'dobj' (spaCy v2).
            # We check both for compatibility.
            obj_tokens = [c for c in verb.children if c.dep_ in ('obj', 'dobj')]

            # Skip this verb if it has no direct object — it's intransitive
            # in this usage (e.g. "the varnish dries" has no object)
            if not obj_tokens:
                continue

            # --- Build the context window -----------------------------------
            # Instead of using spaCy's sentence boundaries (which are often
            # too short for this archaic text), we take a 300-character window
            # centred on the subject token. This gives enough context to
            # understand each result without flooding the output with entire
            # long recipe paragraphs.
            window    = 300
            ctx_start = max(0, token.idx - window)              # don't go before start of text
            ctx_end   = min(len(text), token.idx + len(token.text) + window)  # don't go past end
            sentence  = text[ctx_start:ctx_end].strip()

            # Flag whether this is a passive construction
            is_passive = token.dep_ == 'nsubjpass'

            # --- Record each object -----------------------------------------
            for obj_tok in obj_tokens:

                # Skip pronoun objects (it, them, itself, …).
                # These refer back to something mentioned earlier (coreference)
                # and are meaningless without knowing what they refer to.
                # Resolving them would require a coreference model.
                if obj_tok.pos_ == 'PRON':
                    continue

                # Expand from the head token to the full noun phrase.
                # e.g. the head token 'sheen' expands to 'a fine sheen'
                obj_text = noun_chunk_for(obj_tok, doc)

                # Check whether the object is itself a tagged entity
                obj_match = tightest_subject_span(obj_tok, spans)
                obj_tag   = obj_match[1] if obj_match else ''

                # Store the complete triple as a dictionary
                results.append({
                    'div_id':        div_id,         # folio/entry identifier
                    'categories':    categories,     # recipe category (varnish, casting, …)
                    'subject_tag':   subject_tag,    # XML tag of the subject (m, tl, pro, …)
                    'subject_label': TAG_LABELS.get(subject_tag, subject_tag),  # readable label
                    'subject_term':  subject_term,   # full text of the tagged subject span
                    'verb_lemma':    verb_lemma,     # dictionary form of the verb
                    'verb_form':     verb.text,      # inflected form as it appears in text
                    'passive':       is_passive,     # True if this is a passive construction
                    'obj_text':      obj_text,       # full noun phrase of the direct object
                    'obj_tag':       obj_tag,        # XML tag of the object (if tagged)
                    'sentence':      sentence,       # surrounding text for context
                })

    print(f"\nFound {len(results):,} triples across {ab_count:,} paragraphs.",
          flush=True)

    # =============================================================================
    # WRITE OUTPUT FILES
    # =============================================================================

    # -------------------------------------------------------------------------
    # Detail CSV — one row per triple
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Summary CSV — aggregated by (tag, term, verb)
    # -------------------------------------------------------------------------
    # For each unique combination of (subject tag, subject term, verb lemma),
    # count how many times it appears and list all the objects seen.
    print(f"Writing {OUTPUT_SUMMARY} …")

    # defaultdict(lambda: defaultdict(int)) creates a two-level dictionary:
    #   counts[key][object_text] = number of times that object was seen
    # The 'lambda: defaultdict(int)' means missing inner keys start at 0.
    counts: dict = defaultdict(lambda: defaultdict(int))
    for r in results:
        key = (r['subject_tag'], r['subject_label'], r['subject_term'], r['verb_lemma'])
        counts[key][r['obj_text']] += 1

    with open(OUTPUT_SUMMARY, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['subject_tag', 'subject_label', 'subject_term',
                    'verb_lemma', 'total_count', 'objects'])

        # Sort rows alphabetically by label, then term, then verb
        for key in sorted(counts, key=lambda x: (x[1].lower(), x[2].lower(), x[3])):
            tag, label, term, verb = key
            obj_counts = counts[key]
            total = sum(obj_counts.values())

            # Build a readable list of objects with counts where > 1.
            # e.g. "the fire (3); rain; the mold"
            obj_list = '; '.join(
                f"{o} ({n})" if n > 1 else o
                for o, n in sorted(obj_counts.items(), key=lambda x: (-x[1], x[0]))
            )
            w.writerow([tag, label, term, verb, total, obj_list])

    # -------------------------------------------------------------------------
    # Caveats report
    # -------------------------------------------------------------------------
    # Collect per-tag counts and passive count to include in the report
    tag_counts: dict = defaultdict(int)
    for r in results:
        tag_counts[r['subject_tag']] += 1

    passive_count = sum(1 for r in results if r['passive'])

    write_caveats(tag_counts, passive_count, ab_count, len(results))
    print("Done.")


# =============================================================================
# CAVEATS REPORT
# =============================================================================

def write_caveats(tag_counts, passive_count, ab_count, total_triples):
    """Write a Markdown file documenting the methodology and limitations."""
    print(f"Writing {OUTPUT_CAVEATS} …")

    # Build the per-tag results table for the report
    tag_rows = []
    for tag in sorted(TAG_LABELS, key=lambda t: TAG_LABELS[t]):
        n = tag_counts.get(tag, 0)
        tag_rows.append(f"| `<{tag}>` | {TAG_LABELS[tag]} | {n} |")
    tag_table = '\n'.join(tag_rows)

    # f-string: curly braces insert Python values into the string
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
| `sentence` | 300-character context window around the subject token |

### `subject_verb_obj_summary.csv`

One row per unique `(subject_tag, subject_term, verb_lemma)` group, with
all attested objects listed in the `objects` column (frequency in
parentheses if > 1).
"""

    with open(OUTPUT_CAVEATS, 'w', encoding='utf-8') as f:
        f.write(report)


# =============================================================================
# ENTRY POINT
# =============================================================================
# This block only runs when the script is executed directly (not when it is
# imported as a module by another script). It calls main() to start the analysis.
if __name__ == '__main__':
    main()
