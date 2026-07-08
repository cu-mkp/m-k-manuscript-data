# Workplan — print production remediation

**Source of findings:** [`qc/print-audit/PRINT-AUDIT.md`](PRINT-AUDIT.md) — *Print production audit of `all_tl_figures.pdf`*, 2026-07-08, produced by Claude Fable 5 in session with @tcatapano; audited the 748-page PDF at commit `4d87b147` on branch `issue2121`, pipeline `lib/generate_pdf_gemini.py` → WeasyPrint 69.0 → `post_process_pdf_links()`. Root-cause identifiers (**R1**–**R11**) below refer to that document's numbering and are stable — quote them in commit messages and issue titles.

**Scope.** Four generated PDFs share this pipeline: `all_tl_figures.pdf`, `all_tcn_figures.pdf`, `metadata/glossary.pdf`, `metadata/entry-metadata.pdf`. Except where noted, a fix to `lib/generate_pdf_gemini.py` benefits the two manuscript PDFs; `lib/branding.py`, `lib/generate_glossary_pdf.py` and `lib/generate_entry_metadata_pdf.py` need the same treatment for R2/R7/R9.

**Rebuild cost.** Each manuscript variant takes ≈6 min to render; a full four-PDF regeneration ≈20 min. Batch changes per phase rather than rebuilding per commit.

---

## Phase 0 — Data corrections (no code, unblocks everything)

Can proceed in parallel with Phase 1; touches source data, not the pipeline.

| # | Task | Root cause | Files | Verification |
|---|---|---|---|---|
| 0.1 | Fix three malformed `<i>` tags in the comment CSV: *Bargeo…* (`<i>` for `</i>`, twice), *Cf., the modern Greek `<i>όφις<i/>`*, *Girolamo Mercuriale, `<i>Liber responsorum…`* (unclosed) | [R1] | `metadata/DCE_comment-tracking-Tracking.csv` | `grep -c '<i'` vs `'</i>'` balance per row |
| 0.2 | Correct the three unresolvable essay `entry-id`s | *(pre-existing, [#2129](https://github.com/cu-mkp/m-k-manuscript-data/issues/2129))* | `metadata/annotation-metadata.csv` | build prints no `normalize_entry_id` warning |
| 0.3 | Decide the disposition of the XML encoding anomalies | *(pre-existing, [#2133](https://github.com/cu-mkp/m-k-manuscript-data/issues/2133))* | `ms-xml/{tl,tc,tcn}/` | audit script in #2133 |

> 0.1 also benefits the online edition, which consumes the same CSV — the same three notes italicise everything after them in any consumer that renders the field as HTML.

---

## Phase 1 — Blocks printing (target: one PR, one rebuild)

These are the four changes that clear the majority of visible defects. All are small; the risk is in the rebuild, not the edit.

### 1.1 — Balance inline tags in endnote text · [R1] · 🔴
* **Change:** route `comment_text` through the existing `balance_inline_tags()` before interpolation in the endnotes assembly of `xml_to_html()`.
* **Why now:** a data typo currently costs 205 pages, not one note. Ship this *with* 0.1 so the defect is fixed at both ends.
* **Verify:** `<i>` opens == closes in the emitted HTML; no page beyond p.543 is ≥85% italic (script: reuse the pdfplumber loop from the audit).
* **Effort:** 1 line + test.

### 1.2 — Page numbers and running heads · [R2] · 🔴
* **Change:** `@page` margin boxes in `get_css()`; suppress on `:first`. Add `string-set` on `.head` for a running head naming the current entry. Same treatment in `generate_glossary_pdf.py` and `generate_entry_metadata_pdf.py`.
* **Open question for the team:** do the TOC and the two indexes need *page* references (WeasyPrint `target-counter(attr(href), page)`), or do folio references suffice for a reference work whose canonical citation is by folio? This is an editorial decision, not a technical one — it determines whether 1.2 is ~10 lines or a two-pass build.
* **Verify:** every page after the first bears a number; TOC/index entries resolve; check the last page of each section for an off-by-one running head.
* **Effort:** small if folio references stand; medium if page references are wanted.

### 1.3 — Remove `page-break-inside: avoid` from entries · [R6] · 🟠
* **Change:** drop it from `.entry` and `.margin-notes`; retain on `.fig-inline`, `.fig-with-note`. Add `.head { break-after: avoid }` and `orphans/widows: 2` on `p, .ab`.
* **Verify:** re-run the trailing-void measurement (177/538 pages > 2 in today; expect < 20); confirm no heading sits in the bottom 1.5 in with fewer than ~90 characters following (7 today).
* **Effort:** 4 lines. Expect the page count to *drop* materially — this is also the paper-cost fix.

### 1.4 — Deterministic font resolution · [R4] + [R5] · 🟠
* **Change:** remove `"Garamond"` and `"Times New Roman"` from the body stack (neither is bundled; both are silent-substitution hazards). Remove `font-family: monospace` from `.endnote-id` and `.ms`, or bundle a monospace face and name it.
* **Verify:** the font inventory contains **only** Georgia (4 faces), Helvetica Neue, DejaVu Sans (2), Noto Sans Symbols. Confirm `ʒ ʘ ☼ ♀ ὗ` now render in DejaVu/Noto alongside `℥ ☿ ☾`.
* **Effort:** 2 lines. Reproducibility payoff: the current build depends on which fonts happen to be installed on the build host.

**Phase 1 exit criteria:** rebuild all four PDFs; re-run `step1_checks.py` and `step1_glyphs_images.py`; italic-leak, void, and font-inventory checks pass; spot-rasterise pp. 3, 8, 207, 544, 665.

---

## Phase 2 — Archival deposit

### 2.1 — Preserve document metadata through post-processing · [R9] · 🟡
* **Change:** in `post_process_pdf_links()`, carry `reader.metadata` onto the writer, restore `/Lang` from the source catalog, set `/Title` per document. (Verified: WeasyPrint emits `/Title` and `/Lang`; `PdfWriter().append()` discards both.)
* **Verify:** `/Title`, `/Lang`, `/Producer` present in all four PDFs.
* **Effort:** ~5 lines.

### 2.2 — Language tagging on foreign-language spans · [R8, part] · 🟡
* **Change:** emit `lang="fr|la|it|el|oc|po"` on the corresponding semantic spans in `process_element()`. Prerequisite for correct hyphenation *and* for PDF/UA text extraction.
* **Verify:** `lang="fr"` count > 0 in the tl HTML; spot-check a Latin phrase.
* **Effort:** small (one mapping dict).

### 2.3 — PDF/A conformance · 🟡 · **scope first, then estimate**
* Not attempted in the audit. Needs a decision on target (PDF/A-2b is the usual deposit level), an `/OutputIntents` ICC profile, XMP metadata, and validation with veraPDF. Ghostscript's `-dPDFA` is the pragmatic route but will re-encode the 165 images — interacts with **R3**.
* **Recommend:** defer until R3 is resolved, or the images will be converted twice.

---

## Phase 3 — Print quality

| # | Task | Root cause | Notes |
|---|---|---|---|
| 3.1 | Print stylesheet: links black and un-underlined, hide the 991 `↩` back-links, greyscale the footnote refs and margin-note tints | [R7] | **Decision needed:** is the deposit copy colour or greyscale? Colour is defensible for a digital-first edition; it should be a recorded choice, not an accident of the screen CSS. |
| 3.2 | `hyphens: auto` + `orphans`/`widows` | [R8] | **Blocked by 2.2** — enabling hyphenation before language tagging would hyphenate French and Latin by English rules. |
| 3.3 | Whitespace around inline markers (`[94]Emeralds`, `Nico[illegible] Costé`) | [R10] | Cosmetic; a hair space after a `comment` marker that abuts a word character. |
| 3.4 | Linkify and break-safe the raw URLs in endnote text | [R11] | Makes them clickable *and* stops `https:// edition640…` breaking after the scheme. |

---

## Phase 4 — Out of pipeline

### 4.1 — Figure resolution · [R3] · 🔴 for deposit, **not solvable in CSS**
123 of 165 placements are below 300 PPI (48 below 150); the source PNGs on the asset server are screen derivatives and the pixels do not exist. Options, in order of preference:

1. Re-derive `images/` from the project's source facsimile photography at ≥300 PPI for the printed size.
2. Accept and **document** the resolution in the print edition's colophon; do not claim 300 PPI compliance in the deposit record.
3. Reduce printed figure sizes to reach 300 PPI — rejected: it would shrink several figures below legibility.

Related: `fig_p020r_1` is absent from the asset server entirely and currently sourced via a Google Drive fallback (noted in [#2125](https://github.com/cu-mkp/m-k-manuscript-data/issues/2125)); it needs uploading regardless.

**Owner:** this is Naomi/Pamela's call, not a pipeline task. Suggest raising it as its own issue with the audit's PPI table attached.

---

## Sequencing rationale

```
Phase 0 (data)  ─┐
                 ├─► Phase 1 (blocks printing) ──► rebuild ──► re-audit
Phase 1.1 needs ─┘
                        │
                        ├─► Phase 2 (deposit)  ──► 2.3 blocked by 4.1
                        └─► Phase 3 (quality)  ──► 3.2 blocked by 2.2
```

* **0.1 and 1.1 ship together** — the data fix and the guard that makes the data fix non-load-bearing.
* **Phase 1 is one rebuild.** Don't regenerate between 1.1/1.2/1.3/1.4.
* **4.1 gates 2.3.** Running Ghostscript's PDF/A conversion before the images are re-derived means converting them twice.
* **2.2 gates 3.2.** Hyphenation without language tags is worse than no hyphenation.

## Issues to file

| Title | Covers | Assign |
|---|---|---|
| Print audit R1: unclosed `<i>` in three endnote comments italicises 205 pages | 0.1, 1.1 | pipeline |
| Print audit R2: generated PDFs have no page numbers or running heads | 1.2 | pipeline + editorial decision |
| Print audit R6: `page-break-inside: avoid` leaves 177 pages part-blank | 1.3 | pipeline |
| Print audit R4/R5: non-deterministic font resolution | 1.4 | pipeline |
| Print audit R9: post-processing strips `/Title` and `/Lang` | 2.1 | pipeline |
| Print audit R3: manuscript figures are below print resolution | 4.1 | @njr2128 / @ps2270 |
| Print audit R7/R8/R10/R11: print stylesheet and typography | Phase 3 | pipeline |

Cross-reference the umbrella issue [#2121](https://github.com/cu-mkp/m-k-manuscript-data/issues/2121) and cite `qc/print-audit/PRINT-AUDIT.md` §R*n* in each.
