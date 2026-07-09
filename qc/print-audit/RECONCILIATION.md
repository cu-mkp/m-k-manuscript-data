# Reconciliation of the two print production reviews

Two independent reviews of the same PDFs were produced on 2026-07-08:

| | Review | Tooling | Scope |
|---|---|---|---|
| **A** | [`qc/reports/pdf-production-review.md`](../reports/pdf-production-review.md) | Ghostscript (`nullpage`, bbox scan, PNG render), `identify`, raw object grep. **No** `pypdf`, `pdfplumber`, `PIL`, Poppler | both PDFs (`all_tl_figures`, `all_tcn_figures`), sampled visual review + contact sheets |
| **B** | [`qc/print-audit/PRINT-AUDIT.md`](PRINT-AUDIT.md) | pypdf + pdfplumber (per-glyph font attribution, per-image placement geometry), Ghostscript render | `all_tl_figures` (748 pp), 21-page structural sample |

Findings are labelled **A1–A7 / V1–V6** (review A) and **R1–R11** (review B). Both reviews audited the pre-fix PDFs at commit `4d87b147`.

**Verdict: the reviews agree on every finding they both reached, and each caught defects the other missed.** Review A's tooling constraints (no per-glyph or per-image introspection) explain most of its blind spots; review B's narrower page sample explains most of its own. Together they are stronger than either alone.

---

## 1. Corroborated — both reviews, independently

| Finding | A | B | Agreement |
|---|---|---|---|
| Page geometry uniform (612×792, no rotation, Trim=Bleed=Media) | A1 | Step 1 table | Exact. Both note no bleed, correct for this trim. |
| No rendering errors / no content overflow | A2 | Step 1 (0 overflow) | Exact, by different methods (gs `nullpage` vs. per-char bbox). |
| Fonts embedded and subset | A3 | Step 1 (12 faces) | Exact — 12 faces, all subset. |
| Document metadata too thin; `post_process_pdf_links()` is the cause | A4 | **R9** | Exact, including the same root cause. B additionally *proved* it experimentally (WeasyPrint emits `/Title` + `/Lang`; `PdfWriter.append()` discards both). |
| No page numbers or running heads | V3 | **R2** | Exact, same proposed `@page` remedy and title-page suppression. |
| Over-broad `page-break-inside: avoid` strands headings and empties pages | V1, V2, V5 | **R6** | Exact, same root cause and remedy (`break-after: avoid` on `.head`, orphans/widows, keep only atomic objects together). |
| No tables → table-fragmentation not a risk | A7 | "Not found" | Exact. |
| Links/bookmarks present at object level | A6 | Step 1 | Exact. |

Both reviews independently identified **p.4 of `all_tl_figures.pdf`** as the worst page (A: "heading-only page"; B: 8.6 in of trailing white space — the largest void measured).

---

## 2. Found only by review B (pypdf/pdfplumber)

| # | Finding | Why A missed it |
|---|---|---|
| **R1** | **An unclosed `<i>` in three endnote comments italicised 205 pages (27% of the document), including all three indexes in full.** | A rendered index pages (TL 700, 731, 748) and described them as "columns/lists with many links" without registering that the type was italic. Detecting this reliably needs per-glyph font attribution — A had no `pdfplumber`. This was the single largest defect in the document. Fixed in `60f96a39`. |
| **R3** | 123 of 165 image placements below 300 PPI (48 below 150; min 96). | A counted image *objects* but could not measure placement geometry without `pdfimages`/`pdfplumber`, so it could only recommend "validate source image dimensions" as a future check. B computed effective PPI per placement. |
| **R4** | Manuscript symbols split across three fonts — `ʒ ʘ ☼ ♀` in Times New Roman, `℥ ☿ ☾` in DejaVu — because `"Times New Roman"` precedes the bundled fallbacks in the stack. | A listed both fonts in its inventory (A3) and flagged reproducibility, but had no way to see *which glyphs* landed in which face. |
| **R5** | `font-family: monospace` resolves to **Verdana-Italic** — an italic face for a non-italic element — across the 90-page endnote section. | Same cause: A saw "Verdana Italic" in the font list and did not ask why an italic face was present. |
| **R10** | Whitespace artefacts around inline markers (`[94]Emeralds`, `Nico[illegible] Costé`). | Below the resolution of a sampled visual review at 110 dpi. |
| **R11** | Raw URLs in endnote text, breaking after `https://`. | Not sampled. |

---

## 3. Found only by review A (Ghostscript + raw object scan)

| # | Finding | Verified by B? | Assessment |
|---|---|---|---|
| **A5** | **No `/OutputIntent` or ICC profile; all images `/DeviceRGB`; 153 `/SMask` soft masks.** Transparency and colour management are unaddressed for print-shop delivery. | **Yes** — re-measured: 165 unique image XObjects, **153 with `/SMask`**, **165 DeviceRGB**, no `/OutputIntents`. | **Genuinely additive and important.** B checked for `/OutputIntents` but never inspected colour space or transparency. Soft masks can flatten unpredictably on older RIPs. Escalates B's R9 from "metadata" to "metadata + colour/transparency policy". |
| **V6** | Title page uses `height: 8.5in` with `padding: 2em` and a border, **no `box-sizing: border-box`** — fragile to any content or font change. | **Yes** — confirmed: `.title-page { border: 1px solid black; padding: 2em; height: 8.5in; }`, and `box-sizing` appears **zero** times in the stylesheet. | **Genuinely additive.** B never examined the title page's CSS because it rendered correctly. A latent overflow bug, and the DCE branding header/footer added in `4d87b147` puts *more* content in that fixed-height box. |
| **V4** | Back-matter index pages are visually sparse and uneven. | Partly. B's void measurement covered the translation body only (pp. 3–540); it did not quantify the indexes. | **Additive scope.** Worth re-measuring the indexes after R1's fix, which changed their pagination. |
| **A6** | Suggests automated internal-link + external-URL validation in CI. | — | Additive process recommendation. |
| — | A full **suggested automated build-check list** (sparse-page detector, bbox consistency, font-embedding gate, missing-asset gate, contact sheets per build). | — | Additive and worth adopting; B produced ad-hoc scripts (`step1_checks.py`, `step1_glyphs_images.py`) that are the natural starting point. |

---

## 4. Apparent contradictions (all resolve)

| Claim | Resolution |
|---|---|
| A: "318 image objects"; B: "165 image placements" | Both correct, counting different things. B counts unique image XObjects (165); A's raw grep counted image objects **plus** their 153 soft-mask objects: 165 + 153 = 318. Verified. |
| A: "294 external URI strings"; B: "282 external links (page-1 annotations aside)" | Both correct: A counted URI *strings* in the raw object stream; B counted `/URI` link **annotations**. Repeated URLs in endnote text account for the difference. |
| A: "Fonts … Pass with reproducibility caveat" | Correct as far as it goes, but B shows two of those fonts are the *result* of silent substitution (R4, R5), not deliberate choices. A's caveat is right; its severity is understated. |

No factual conflict was found between the two reviews.

---

## 5. Consequences for the workplan

[`WORKPLAN.md`](WORKPLAN.md) is updated to absorb review A's additive findings:

* **New R12 — colour management and transparency** (from A5). Belongs with R9 in Phase 2, and *gates* the PDF/A decision alongside R3: converting 165 RGB images with soft masks to a print profile is a decision to make once, after the images are re-derived.
* **New R13 — title-page CSS fragility** (from V6). Cheap fix (`box-sizing: border-box; min-height`), rising in importance now that the branding header and footer share that fixed-height box.
* **R6 extended to back matter** (from V4): re-measure index-page fill after the R1 fix before tuning column rules.
* **Phase 5 added — automated build checks** (from A's final section), seeded with `step1_checks.py` and `step1_glyphs_images.py`.

## 6. Method note, for the next review

Review A explicitly recorded that `pypdf`, `pdfplumber`, `PIL`, and Poppler were unavailable in its environment. That single constraint accounts for missing the document's largest defect (R1), its print-blocking image resolution (R3), and both font bugs (R4, R5). The tools are a one-line install (`uv pip install pypdf pdfplumber`, as used for review B). **Any future audit of these PDFs should install them first.** Conversely, review A's raw-object grep surfaced the transparency and colour-space issues that B's higher-level API never looked at — both layers of inspection earn their place.
