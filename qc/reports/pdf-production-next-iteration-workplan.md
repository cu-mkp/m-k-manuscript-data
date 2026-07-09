# PDF Production Next Iteration Workplan

Drafted by: Codex, based on `reports/pdf-production-review.md`

Date: 2026-07-08

Scope: layout, production quality, PDF correctness, and reproducibility for the XML -> Python -> HTML/CSS -> WeasyPrint pipeline. Do not rewrite editorial content.

## Objective

Move both generated PDFs from **needs another layout pass** toward **nearly ready** by addressing the recurring layout defects found in the production review, then adding repeatable checks so regressions are visible in later builds.

Target files:

- `all_tcn_figures.pdf`
- `all_tl_figures.pdf`

Primary generator likely to change:

- `lib/generate_pdf_gemini.py`

## Priority Order

### 1. Fix Pagination Keep Rules

Goal: eliminate stranded headings and very sparse carryover pages.

Actions:

- Relax `.entry { page-break-inside: avoid; }`.
- Add `break-after: avoid` to `.head` and `.head.minor-head`.
- Add `orphans` and `widows` rules to `.ab`, `.endnote`, and `.margin-note`.
- Keep only genuinely small/atomic blocks together.

Validation:

- Recheck known problem pages from the review:
  - `all_tcn_figures.pdf`: pages 4, 73, 225, 288, 564, 693, 704, 777, 986
  - `all_tl_figures.pdf`: page 4 and sampled sparse pages around 140 and 731
- Compare before/after sparse-page counts using Ghostscript bbox output.

### 2. Retune Margin-Note Break Behavior

Goal: keep notes readable without forcing entire note groups onto fresh pages.

Actions:

- Allow `.margin-notes` containers to split between child `.margin-note` blocks.
- Keep individual short `.margin-note` blocks together where possible.
- Avoid unbreakable note groups that are taller than the remaining page area.

Validation:

- Render note-heavy sampled pages and adjacent pages.
- Confirm no clipped notes, overlapped figures, or separated note labels.

### 3. Add Running Heads and Page Numbers

Goal: improve print navigation and proofing for long PDFs.

Actions:

- Add `@page` margin boxes with `counter(page)`.
- Add a short running title or section label.
- Suppress page furniture on the title page with a named page rule.

Validation:

- Render title page, TOC, first body page, dense body page, endnotes, indexes, and final page.
- Confirm page numbers do not collide with content and are absent from the title page.

### 4. Regenerate and Compare PDFs

Goal: make layout changes measurable.

Actions:

- Regenerate both PDFs from the same source inputs.
- Record before/after:
  - page count
  - file size
  - bbox sparse-page count
  - Ghostscript full-render result
  - contact sheet samples

Validation:

- Ensure both PDFs still complete Ghostscript `nullpage` rendering.
- Inspect contact sheets before accepting layout changes.

### 5. Add Automated PDF QA Checks

Goal: make future production review repeatable.

Actions:

- Add or formalize a print-audit script for:
  - page count
  - page-box consistency
  - rotation
  - embedded-font check
  - missing image refs
  - Ghostscript render check
  - bbox sparse-page detector
  - deterministic preview/contact-sheet generation

Validation:

- Run the audit on both PDFs.
- Store or print a stable summary suitable for CI logs.

### 6. Improve PDF Metadata

Goal: preserve bibliographic and build provenance metadata after pypdf post-processing.

Actions:

- In `post_process_pdf_links()`, preserve existing metadata or explicitly set metadata before `writer.write()`.
- Include at minimum:
  - Title
  - Creator/build tool
  - Subject
  - Keywords
  - language/output variant
  - deterministic creation/modification policy

Validation:

- Confirm metadata survives after link post-processing.
- Recheck with `pdfinfo` when Poppler is available.

### 7. External Preflight

Goal: decide print-readiness after layout stabilizes.

Actions:

- Run Acrobat Preflight or equivalent for:
  - output intent
  - RGB/transparency policy
  - PDF/A or PDF/X target if required
  - font embedding
  - annotation/link validity
  - accessibility/tagging expectations

Validation:

- Capture preflight report and document pass/fail decisions.

## Acceptance Criteria

- No heading-only body pages in sampled/known-problem locations.
- Sparse-page count is materially reduced or each remaining sparse page is documented as intentional.
- Body/back-matter pages have usable page numbers and running context.
- Ghostscript full render passes for both PDFs.
- Fonts remain embedded.
- Image references remain complete.
- Production report can be updated from automated audit output rather than manual reconstruction.

## Tracking Citation

This plan cites the prior review by Codex: `reports/pdf-production-review.md`, generated 2026-07-08, especially findings V1-V5 and A4-A6.

