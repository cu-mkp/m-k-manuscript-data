# NLP Analysis — Caveats and Methodology Notes

**Date:** 2026-02-26
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
- `<ab>` blocks processed: 1,767 (of 1,767 that contained at least one tracked tag)
- Triples found: 314
- Passive-voice triples: 0 (0.0%)

**Results per tag type:**

| Tag | Label | Triples |
|-----|-------|---------|
| `<al>` | Animal | 11 |
| `<bp>` | Body Part | 0 |
| `<cn>` | Currency | 0 |
| `<df>` | Definition | 2 |
| `<env>` | Environment | 3 |
| `<m>` | Material | 138 |
| `<ms>` | Measurement | 15 |
| `<md>` | Medical Term | 0 |
| `<mu>` | Musical Instrument | 0 |
| `<pn>` | Personal Name | 7 |
| `<pl>` | Place | 16 |
| `<pa>` | Plant | 5 |
| `<pro>` | Profession | 52 |
| `<sn>` | Sense Term | 8 |
| `<tmp>` | Temporal | 2 |
| `<tl>` | Tool | 33 |
| `<wp>` | Weapon | 22 |

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
