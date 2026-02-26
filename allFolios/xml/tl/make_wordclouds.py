#!/usr/bin/env python3
"""
Generate word clouds from subject_verb_obj_detail.csv.

One cloud per tag type that has results.  Each cloud shows verb lemmas
sized by frequency (how often entities of that type perform that action),
with the object appended in lighter text as "verb · object" phrases.

Two outputs per tag:
  - Individual PNG:  wordclouds/<tag>_<label>.png
  - Combined grid:   wordclouds/all_tags_grid.png

Usage
-----
    ~/nlp-venv/bin/python make_wordclouds.py
"""

import os
import csv
import math
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from wordcloud import WordCloud

DETAIL_CSV  = "subject_verb_obj_detail.csv"
OUT_DIR     = "wordclouds"

# Colour palette — one per tag label, cycling if more than palette size
TAG_COLORS = {
    'Material':          '#1f77b4',
    'Profession':        '#d62728',
    'Tool':              '#2ca02c',
    'Weapon':            '#ff7f0e',
    'Place':             '#9467bd',
    'Measurement':       '#8c564b',
    'Animal':            '#e377c2',
    'Sense Term':        '#7f7f7f',
    'Personal Name':     '#bcbd22',
    'Plant':             '#17becf',
    'Environment':       '#aec7e8',
    'Temporal':          '#ffbb78',
    'Definition':        '#98df8a',
    'Body Part':         '#ff9896',
    'Currency':          '#c5b0d5',
    'Medical Term':      '#c49c94',
    'Musical Instrument':'#f7b6d2',
}
DEFAULT_COLOR = '#555555'


def make_colormap(hex_color):
    """Return a wordcloud color_func that uses a single hue with varying lightness."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        # Vary lightness: larger words darker, smaller lighter
        factor = 0.55 + random_state.uniform(0, 0.35)
        return (int(r * factor), int(g * factor), int(b * factor))

    return color_func


def load_data(csv_path):
    """Return dict: tag_label -> list of (verb_lemma, obj_text)."""
    data = defaultdict(list)
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            label = row['subject_label']
            verb  = row['verb_lemma'].strip().lower()
            obj   = row['obj_text'].strip().lower()
            if verb:
                data[label].append((verb, obj))
    return data


def build_frequencies(pairs):
    """
    Build two frequency dicts from (verb, obj) pairs:
      verb_freq  — verb lemma counts
      phrase_freq — "verb · object" phrase counts (where object is non-empty)
    """
    verb_freq   = defaultdict(int)
    phrase_freq = defaultdict(int)
    for verb, obj in pairs:
        verb_freq[verb] += 1
        if obj:
            phrase = f"{verb} · {obj}"
            phrase_freq[phrase] += 1
    return dict(verb_freq), dict(phrase_freq)


def make_cloud(freq_dict, color_func, width=800, height=400, max_words=80):
    """Generate and return a WordCloud object."""
    wc = WordCloud(
        width=width,
        height=height,
        background_color='white',
        max_words=max_words,
        prefer_horizontal=0.85,
        color_func=color_func,
        collocations=False,
        min_font_size=10,
    )
    wc.generate_from_frequencies(freq_dict)
    return wc


def save_individual(wc, label, tag, out_dir):
    """Save a single cloud as PNG."""
    safe_label = label.lower().replace(' ', '_')
    path = os.path.join(out_dir, f"{tag}_{safe_label}.png")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f"{label}  ‹{tag}›", fontsize=14, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return path


def save_grid(clouds_info, out_dir):
    """
    Save all clouds in a single grid figure.
    clouds_info: list of (label, tag, WordCloud)
    """
    n     = len(clouds_info)
    ncols = 2
    nrows = math.ceil(n / ncols)

    fig = plt.figure(figsize=(18, 5 * nrows))
    fig.suptitle(
        "Transitive verb clouds by entity type\n(word size ∝ frequency)",
        fontsize=16, fontweight='bold', y=1.01
    )
    gs = gridspec.GridSpec(nrows, ncols, figure=fig, hspace=0.45, wspace=0.1)

    for idx, (label, tag, wc) in enumerate(clouds_info):
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(gs[row, col])
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f"{label}  ‹{tag}›", fontsize=12, fontweight='bold')

    # Hide any leftover empty subplots
    for idx in range(n, nrows * ncols):
        row, col = divmod(idx, ncols)
        fig.add_subplot(gs[row, col]).axis('off')

    path = os.path.join(out_dir, "all_tags_grid.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Reading {DETAIL_CSV} …")
    data = load_data(DETAIL_CSV)

    if not data:
        print("No data found — run m_subject_verbs.py first.")
        return

    # Sort by label for consistent ordering
    sorted_labels = sorted(data.keys())
    clouds_info   = []   # (label, tag, WordCloud) for the grid

    for label in sorted_labels:
        pairs = data[label]
        if not pairs:
            continue

        # Infer tag from the detail CSV (first row matching label)
        tag = label.lower().replace(' ', '_')   # fallback
        # Re-read to get tag abbreviation
        with open(DETAIL_CSV, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['subject_label'] == label:
                    tag = row['subject_tag']
                    break

        verb_freq, phrase_freq = build_frequencies(pairs)

        # Use verb-only frequencies; skip if only 1 unique verb (trivial cloud)
        if len(verb_freq) < 2:
            print(f"  Skipping {label} ({tag}): only {len(verb_freq)} unique verb(s)")
            continue

        color_func = make_colormap(TAG_COLORS.get(label, DEFAULT_COLOR))
        wc = make_cloud(verb_freq, color_func)

        path = save_individual(wc, label, tag, OUT_DIR)
        clouds_info.append((label, tag, wc))
        n_triples = len(pairs)
        print(f"  {label:20s} ({tag:4s})  {n_triples:3d} triples  →  {path}")

    if clouds_info:
        grid_path = save_grid(clouds_info, OUT_DIR)
        print(f"\nGrid saved → {grid_path}")

    print(f"\nDone. {len(clouds_info)} clouds written to ./{OUT_DIR}/")


if __name__ == '__main__':
    main()
