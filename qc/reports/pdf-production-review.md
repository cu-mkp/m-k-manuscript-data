# PDF Production Review

Date: 2026-07-08

Reviewed files:

- `all_tcn_figures.pdf` — 61,266,567 bytes, 1003 pages
- `all_tl_figures.pdf` — 61,246,061 bytes, 748 pages

Scope: production/layout/prepress review only. Editorial content was not rewritten or changed. No source files were modified.

## Overall Verdict

**Needs another layout pass.**

The PDFs are structurally renderable and have consistent page geometry, embedded subset fonts, working outline/link structures at the object level, and no Ghostscript rendering failures. They are not yet production-ready for print-quality release because pagination quality is uneven: both files contain stranded headings, very sparse carryover pages, and no running heads or physical page numbers. The main recurring issue appears to be over-broad `page-break-inside: avoid` / `break-inside: avoid` behavior in the WeasyPrint CSS and HTML grouping.

## Method

### Automated Whole-PDF Scan

Available tools used: `gs`, `identify`, `python3`, `rg`, `find`, `sed`, `montage`.

Unavailable or unusable in this environment:

- `pdfinfo`, `pdffonts`, `qpdf`, `mutool`, `pdftoppm`, `pdfimages`
- `exiftool` exists but fails with `/usr/bin/perl5.30: bad interpreter`
- Python packages `pypdf`, `pdfplumber`, `PIL`, and `fitz` were not installed in the current Python environment

Checks performed:

- Ghostscript full render to `nullpage`: both PDFs completed with exit code 0.
- Ghostscript page count and page-box inspection.
- Ghostscript bbox scan over every page.
- Raw PDF object scan for metadata, fonts, image objects, annotations, links, color spaces, JavaScript/forms/embedded files.
- HTML/source inspection for CSS, figure refs, margin notes, endnotes, links, and generation code.
- Image reference completeness and source image dimensions.

### Sampled Visual Review

Representative pages were rendered with Ghostscript to PNG previews at 110 dpi. Contact sheets were created at:

- `tmp/pdfs/contact/all_tcn_contact.png`
- `tmp/pdfs/contact/all_tl_contact.png`
- `tmp/pdfs/contact/tcn_adjacent_breaks.png`
- `tmp/pdfs/contact/tl_adjacent_breaks.png`

Sample set included title pages, TOCs, early body pages, figure/note pages, dense text pages, automated bbox outliers, endnotes/index pages, and final pages. This was a sampled layout review, not a full page-by-page proofread.

## Automated Findings Verified Across Whole PDFs

### A1. Page Geometry Is Consistent

- Location: all pages in both PDFs
- Severity: Pass / informational
- Description: Every page is `612 x 792 pt` US Letter. All pages have no CropBox, TrimBox and BleedBox equal to MediaBox, and no rotation.
- Why it matters: Consistent page boxes are required for reproducible print output and downstream imposition.
- Likely cause: `@page { size: letter; margin: 1in; }` in generated CSS.
- Recommended fix: No geometry fix required. If sending to a print shop, confirm whether they require an explicit CropBox/TrimBox/BleedBox convention or PDF/X output.

### A2. No Ghostscript Rendering Errors

- Location: both full PDFs
- Severity: Pass / informational
- Description: `gs -sDEVICE=nullpage` completed for both PDFs without emitted errors.
- Why it matters: This catches some corrupt objects, missing resources, and render-time PDF failures.
- Likely cause: WeasyPrint output plus pypdf post-processing is syntactically acceptable to Ghostscript.
- Recommended fix: Keep this as an automated build check.

### A3. Fonts Appear Embedded and Subset

- Location: both PDFs
- Severity: Pass with reproducibility caveat
- Description: Raw object scan found 12 BaseFont names in each PDF, all subset-prefixed, with 12 `/FontFile2` and 12 `/ToUnicode` entries. Fonts include Georgia, Georgia Bold/Italic variants, DejaVu Sans, DejaVu Sans Bold, Noto Sans Symbols, Times New Roman variants, Helvetica Neue, and Verdana Italic.
- Why it matters: Embedded fonts reduce missing-glyph and print-substitution risk.
- Likely cause: WeasyPrint embedded available system fonts plus explicitly bundled DejaVu/Noto fallback fonts.
- Recommended fix: For reproducible builds across machines, bundle or pin all non-system fonts used by the CSS stack, not only DejaVu/Noto. Verify with `pdffonts` in CI when Poppler is available.

### A4. Metadata Is Too Thin

- Location: document metadata in both PDFs
- Severity: Minor
- Description: Producer is `pypdf`; no Author, Subject, Keywords, Creator, CreationDate, or ModDate were detected. Several outline title strings are present, but document-level metadata is minimal.
- Why it matters: Poor metadata weakens archive ingest, accessibility review, bibliographic identification, and reproducibility.
- Likely cause: `post_process_pdf_links()` rewrites the PDF through `pypdf.PdfWriter`, which likely replaces or drops WeasyPrint metadata unless explicitly copied/set.
- Recommended fix: In `lib/generate_pdf_gemini.py`, preserve metadata from the WeasyPrint output or explicitly set title, language, creator, producer/build version, creation date policy, and subject/keywords during pypdf write.

### A5. No Output Intent; RGB Images and Soft Masks Present

- Location: both PDFs
- Severity: Major for print-shop delivery; Minor for web/PDF reading
- Description: Raw scan found no `/OutputIntent` or `/ICCBased` profile. Both PDFs contain `/DeviceRGB` image/color use, 318 image objects, and 153 `/SMask` objects.
- Why it matters: Print workflows often require color-managed PDF/X or at least explicit RGB/CMYK handling. Soft masks/transparency can cause flattening surprises in older RIPs.
- Likely cause: WeasyPrint-generated screen/PDF output using sRGB PNG assets and transparency in logos/icons/images.
- Recommended fix: For print release, run Acrobat Preflight or Ghostscript/PDF/X conversion review. Decide whether this is intentionally digital-first RGB or needs a print-specific PDF/X-4 or PDF/A profile.

### A6. Link and Bookmark Objects Are Present

- Location: both PDFs
- Severity: Pass with validation gap
- Description: Both PDFs contain outlines, annotations, internal destinations, and 294 detected external URI strings. No JavaScript, forms, XFA, OpenAction, or embedded files were detected.
- Why it matters: Links/bookmarks are central to navigation, but external links can rot and internal link rectangles need viewer compatibility testing.
- Likely cause: WeasyPrint anchors/bookmarks plus `post_process_pdf_links()` in `lib/generate_pdf_gemini.py`.
- Recommended fix: Add automated internal-link validation with `pypdf`/`qpdf` and periodic external URL checks. Test in Acrobat because the generator already notes Acrobat-specific named-destination problems.

### A7. No HTML Tables in These Outputs

- Location: `all_tcn_figures.html`, `all_tl_figures.html`
- Severity: Informational
- Description: No `<table>` elements were found. Table fragmentation is not a current issue for these two PDFs.
- Why it matters: It narrows the likely layout risk to entries, figures, margin notes, endnotes, and indexes.
- Likely cause: Current XML transformation emits structured divs/lists rather than tables.
- Recommended fix: None for tables. Keep a table-specific check if future PDFs include them.

## Visual Findings Verified on Sampled Pages

### V1. Stranded Entry Heading on Page 4

- Location: `all_tcn_figures.pdf` page 4; `all_tl_figures.pdf` page 4
- Severity: Major
- Description: Page 4 contains only the heading "Liste de livres et d'autheurs" / "List of books and authors" plus the folio label and rule. The related content starts on the following page.
- Why it matters: A heading-only page is a poor section break and reads like missing content.
- Likely cause: The `.entry` block has `page-break-inside: avoid`; the following content/margin-note block cannot fit under the heading, so WeasyPrint leaves the heading isolated.
- Recommended fix: Do not apply `page-break-inside: avoid` to every `.entry`. Prefer `break-after: avoid` on `.head`, `orphans`/`widows` on paragraphs, and conditional keep-together only for short entries. If necessary, wrap heading plus first content block in a smaller keep-with-next container.

### V2. Sparse Carryover Pages from Over-Aggressive Keep Rules

- Location: automated bbox outliers and sampled pages:
  - `all_tcn_figures.pdf`: 26 pages below 50k bbox area; 9 tiny pages below 15k area: pages 4, 73, 225, 288, 564, 693, 704, 777, 986
  - `all_tl_figures.pdf`: 6 pages below 50k bbox area; 1 tiny page below 15k area: page 4
- Severity: Major
- Description: Several pages carry only a few lines, a single note box, or a small continuation. Examples: TCN page 73 has a three-line continuation; TCN page 986 has a single short line plus backlink; TL page 140 has one short margin-note box.
- Why it matters: These pages inflate page count and create a visibly uneven book rhythm.
- Likely cause: `.entry`, `.margin-notes`, `.fig-inline`, `.fig-with-note`, index items, and figure/list items all use keep-together rules. When WeasyPrint cannot split a large box gracefully, it pushes content forward and leaves fragments behind.
- Recommended fix: Relax keep rules for long entries and note groups. Use CSS such as `break-inside: auto` for `.entry` by default, `break-inside: avoid` only for short/small entry classes, `break-after: avoid` on headings, and `orphans`/`widows` values on `.ab`, `.endnote`, and `.margin-note`.

### V3. No Running Heads or Physical Page Numbers

- Location: all sampled body/endnote/index pages in both PDFs
- Severity: Major
- Description: Pages show inline manuscript folio labels in headings, but no PDF page number, running head, or footer on body/back-matter pages.
- Why it matters: A 748/1003-page print PDF is hard to cite, proof, review, and navigate without physical folios/page numbers and running context.
- Likely cause: The generated CSS has only `@page { size: letter; margin: 1in; }`; there are no `@top-*` or `@bottom-*` margin boxes, page counters, or named page rules.
- Recommended fix: Add `@page` margin boxes with `counter(page)` and a short running title. Consider suppressing these on the title page with a named page (`.title-page { page: title; } @page title { @bottom-center { content: none; } }`).

### V4. Back-Matter Index Pages Are Visually Sparse and Uneven

- Location: sampled late pages including `all_tcn_figures.pdf` pages 950, 1000, 1003 and `all_tl_figures.pdf` pages 700, 731, 748
- Severity: Minor to Major depending on production standard
- Description: Back-matter pages use columns/lists with many links, but page fill varies substantially. Some pages are acceptable index pages; others look like isolated carryover material.
- Why it matters: Indexes are expected to be scan-friendly and compact. Very sparse back-matter pages increase page count and look unfinished.
- Likely cause: `ul.tag-index-terms li { break-inside: avoid; }`, many short linked items, manual `page-break-before`, and no balancing controls beyond CSS columns.
- Recommended fix: Review column strategy and index break rules. Use smaller top/bottom margins for back matter if acceptable, tune `columns`, and add an automated sparse-page check for index sections.

### V5. Figures and Margin-Note Boxes Render, but Their Keep Behavior Drives Pagination Risk

- Location: sampled figure/note pages including TCN page 500 and TL pages 20, 27, 140
- Severity: Minor for rendering; Major as pagination cause
- Description: Sampled figures and note boxes were not clipped and stayed inside page margins. However, note blocks often occupy large, unbreakable boxes and can create mostly blank pages.
- Why it matters: The visual rendering is acceptable locally, but the box model is too rigid for a long book with hundreds of notes.
- Likely cause: `.margin-notes { page-break-inside: avoid; }` and `.fig-inline { break-inside: avoid; }`.
- Recommended fix: Keep individual figures intact, but allow long `.margin-notes` groups to split between `.margin-note` children. Keep each `.margin-note` together only when short.

### V6. Title Page Fits, but Its CSS Is Fragile

- Location: page 1 in both PDFs
- Severity: Cosmetic / Minor
- Description: The title page renders cleanly in the sampled output. The CSS uses a fixed `.title-page { height: 8.5in; padding: 2em; border: ... }` inside a 9-inch-tall page content area.
- Why it matters: Without `box-sizing: border-box` and an explicit page break/named page, small content or font changes could overflow or alter the page break.
- Likely cause: Fixed-height title-page CSS.
- Recommended fix: Add `box-sizing: border-box; min-height: 8.5in; break-after: page;` or a named title page rule.

## Top 5 Fixes to Make First

1. Relax `.entry { page-break-inside: avoid; }` and replace it with heading keep-with-next plus paragraph `orphans`/`widows`.
2. Allow `.margin-notes` groups to split between `.margin-note` children; keep only short notes together.
3. Add page numbers and running heads via `@page` margin boxes, with suppression on the title page.
4. Add an automated sparse-page detector using Ghostscript bbox output or `pypdf` page content heuristics, failing or warning on pages below a threshold outside intentional section openers.
5. Preserve/set PDF metadata after pypdf link post-processing and add a print-preflight target for output intent/transparency/color decisions.

## Recurring Pattern Problems

- Over-broad keep-together CSS on containers that can be taller than the remaining page area.
- Heading/content separation due to WeasyPrint resolving impossible keep constraints.
- Back matter generated as long linked lists without enough pagination tuning.
- No print-navigation layer: inline manuscript folio labels exist, but generated PDF pages have no folios/running heads.
- Metadata and prepress output intent are not set as part of the reproducible build.

## Likely Source-Level Changes Needed

Primary source inspected: `lib/generate_pdf_gemini.py`.

Likely conservative changes:

- In `get_css()`, change `.entry` from `page-break-inside: avoid` to a less aggressive default such as `break-inside: auto`.
- Add `break-after: avoid` to `.head` and `.head.minor-head`; add `orphans` and `widows` to `.ab`, `.endnote`, and possibly `.margin-note`.
- Replace `.margin-notes { page-break-inside: avoid; }` with child-level keep rules, or add a generated class for short note groups only.
- Add `@page` margin boxes for page numbers/running heads.
- In `post_process_pdf_links()`, copy or set metadata before `writer.write()`.
- Keep figure `break-inside: avoid`, but audit large standalone figures and margin-note figures separately.

No changes were made in this review.

## External Preflight Required

These items require tools not available here or human prepress review:

- Acrobat Preflight: PDF/A or PDF/X conformance, transparency flattening, font embedding confirmation, link annotations, tagged PDF/accessibility.
- veraPDF: PDF/A validation if archival PDF/A is desired.
- qpdf: structural validation, object stream/xref checks, link/name tree inspection.
- Poppler `pdfinfo`/`pdffonts`/`pdfimages`: independent page/font/image inventory.
- Ghostscript or Acrobat color conversion review: RGB/soft mask handling and possible PDF/X-4 output intent.
- Print-shop review: trim/bleed expectations, paper size, color policy, and whether no bleed is acceptable.
- Full human proofing: sampled visual review is not equivalent to checking all 1003 + 748 pages.

## Suggested Automated Build Checks

- Run Ghostscript full render to `nullpage` for each generated PDF.
- Record page count, file size, page-box consistency, rotation, and MediaBox/CropBox/TrimBox/BleedBox summary.
- Run a bbox-based sparse-page detector and emit a page list for review.
- Render a deterministic sample set and contact sheet on every build: front matter, first body pages, figure pages, note-heavy pages, bbox outliers, endnotes, indexes, final pages.
- Validate all image references before WeasyPrint and fail on missing assets.
- Validate source image dimensions and warn when effective print resolution falls below an agreed threshold.
- Use `pdffonts` or a `pypdf`-based check to fail on unembedded fonts.
- Validate internal links/destinations and count unresolved annotations after pypdf post-processing.
- Check for metadata fields and output intent according to release target.
- Add a CSS lint/check that flags broad `page-break-inside: avoid` on large container classes such as `.entry` and `.margin-notes`.

