# NLP Entity-Role Analysis — Ms. Fr. 640

Exploratory analysis of the English translation layer (`all_tl.xml`) of
[BnF Ms. Fr. 640](https://edition640.makingandknowing.org/), encoded by the
[Making and Knowing Project](https://www.makingandknowing.org/) (Columbia University).

**Research question:** For each semantic entity type tagged in the XML
(materials, tools, animals, professions, …), what transitive action verbs
appear when that entity is the grammatical subject of a clause — and what
are the direct objects of those verbs?

---

## Quick start — Google Colab (no setup required)

Click the badge to open the notebook directly in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cu-mkp/m-k-manuscript-data/blob/nlp-analysis/allFolios/xml/tl/ms_fr_640_nlp.ipynb)

Then: **Runtime → Run all**. The notebook installs its own dependencies and
fetches the XML from GitHub — nothing needs to be uploaded or installed locally.

---

## Files

| File | Description |
|------|-------------|
| `ms_fr_640_nlp.ipynb` | Self-contained Colab notebook — start here |
| `m_subject_verbs.py` | Full analysis script for local use |
| `make_wordclouds.py` | Generates per-tag word cloud PNGs |
| `subject_verb_obj_detail.csv` | All 314 subject–verb–object triples |
| `subject_verb_obj_summary.csv` | Aggregated by (tag, term, verb) with object lists |
| `caveats.md` | Detailed methodology notes and known limitations |
| `wordclouds/` | Verb-frequency word clouds, one PNG per tag type |

The two `m_subject_verbs*.csv` files are an earlier pass covering materials only,
retained for reference.

---

## Running locally

### Requirements

- Python 3.10–3.12 (3.14 is not yet supported by spaCy)
- A virtual environment is recommended

### Setup

```bash
python3.12 -m venv nlp-venv
source nlp-venv/bin/activate
pip install spacy lxml wordcloud matplotlib
python -m spacy download en_core_web_sm
```

### Run the analysis

```bash
python m_subject_verbs.py
```

Outputs `subject_verb_obj_detail.csv`, `subject_verb_obj_summary.csv`,
and `caveats.md` in the current directory.

### Generate word clouds

```bash
python make_wordclouds.py
```

Outputs PNGs to `wordclouds/`, including `all_tags_grid.png`.

---

## Method summary

1. The XML is parsed with `lxml`. For each `<ab>` (text block), plain text is
   extracted while the character positions of all 17 semantic tags are tracked.
2. Whitespace is normalised and spans are re-located in the cleaned text.
3. spaCy (`en_core_web_sm`) runs dependency parsing on each block.
4. Tokens with dependency relation `nsubj` or `nsubjpass` are checked against
   tracked spans. Matches whose head verb is transitive (has a direct `obj`
   child) are recorded.
5. Copular verbs and pronoun objects are filtered out.

When tags are nested, `<m>` (Material) takes priority over all other tags;
among other tag types, the tightest (innermost) span wins.

### Tracked tag types

| Tag | Label | Tag | Label |
|-----|-------|-----|-------|
| `<m>` | Material | `<tl>` | Tool |
| `<pa>` | Plant | `<wp>` | Weapon |
| `<al>` | Animal | `<pl>` | Place |
| `<pro>` | Profession | `<pn>` | Personal Name |
| `<bp>` | Body Part | `<env>` | Environment |
| `<md>` | Medical Term | `<sn>` | Sense Term |
| `<ms>` | Measurement | `<tmp>` | Temporal |
| `<cn>` | Currency | `<mu>` | Musical Instrument |
| `<df>` | Definition | | |

---

## Caveats

This is a first-pass exploratory analysis. Key limitations:

- **Model accuracy:** `en_core_web_sm` is trained on modern English; accuracy
  is lower on 16th-century craftsman's prose.
- **Pronoun objects excluded:** *it*, *them*, etc. require coreference
  resolution not available in this model.
- **Direct objects only:** prepositional objects, clausal complements, and
  indirect objects are not captured.
- **Coordinated subjects:** only the `nsubj`-marked conjunct is matched;
  the other may be missed.

See [`caveats.md`](caveats.md) for the full methodology notes.

---

## Citation

If you use this analysis, please cite the Making and Knowing Project:

> Making and Knowing Project, Pamela H. Smith, Naomi Rosenkranz, Tianna
> Uchacz, Tillmann Taape, Clément Godbarge, Sophie Pitman, Jenny Boulboullé,
> Joel Klein, Donna Bilak, Marc Smith, and Terry Catapano, eds.,
> *Secrets of Craft and Nature in Renaissance France. A Digital Critical
> Edition and English Translation of BnF Ms. Fr. 640*
> (New York: Making and Knowing Project, 2020),
> [https://edition640.makingandknowing.org](https://edition640.makingandknowing.org).
