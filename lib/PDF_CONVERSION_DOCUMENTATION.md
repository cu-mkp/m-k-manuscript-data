# BnF Ms. Fr. 640 XML to PDF Conversion Documentation

## Overview

This document describes the complete workflow and features of the `generate_pdf.py` script, which converts the Making and Knowing Project's XML manuscript data into formatted PDF documents.

**Script:** `lib/generate_pdf.py`
**Input:** `allFolios/xml/tl/all_tl.xml` (English translation)
**Output:** `allFolios/pdf/all_tl.html` (intermediate), `allFolios/pdf/all_tl.pdf` (final)

---

## Table of Contents

1. [Conversion Workflow](#conversion-workflow)
2. [Rendering Features](#rendering-features)
3. [Margin Notes Extraction](#margin-notes-extraction)
4. [Styling and Typography](#styling-and-typography)
5. [Dependencies and Setup](#dependencies-and-setup)
6. [Usage](#usage)
7. [Extending the Script](#extending-the-script)

---

## Conversion Workflow

The conversion process follows a three-stage pipeline:

### Stage 1: XML Parsing
```
allFolios/xml/tl/all_tl.xml
           ↓
   [ElementTree Parser]
           ↓
      XML Tree (in memory)
```

- Uses Python's `xml.etree.ElementTree` to parse the manuscript XML
- Validates XML structure
- Creates an in-memory representation of the document tree

### Stage 2: HTML Conversion
```
      XML Tree
           ↓
  [process_element() - Recursive]
           ↓
    - Semantic tagging
    - Margin note extraction
    - Style class assignment
           ↓
  HTML with embedded CSS
           ↓
allFolios/pdf/all_tl.html
```

**Key Process: `process_element(elem, depth, margin_notes)`**

This recursive function traverses the entire XML tree and converts each element to styled HTML:

1. **Identify element type** (structural, semantic, language, transcription)
2. **Apply appropriate HTML wrapper** (`<div>`, `<span>`, `<p>`, etc.)
3. **Add CSS classes** for styling
4. **Extract margin notes** (if applicable)
5. **Process child elements** recursively
6. **Preserve text content** with proper escaping

**Special Behavior:**
- When processing a `<div>` element (manuscript entry), collects all `<ab>` elements with `margin` attributes
- These margin annotations are extracted and appended after the entry as a separate "Margin Notes" section
- Margin position labels (e.g., `[left-middle]`, `[right-top]`) are added for reference

### Stage 3: PDF Generation
```
allFolios/pdf/all_tl.html
           ↓
     [Weasyprint]
           ↓
   - CSS rendering
   - Font embedding
   - Page layout
   - PDF creation
           ↓
allFolios/pdf/all_tl.pdf
```

- Uses weasyprint library to render HTML/CSS as PDF
- Applies print-specific CSS rules (`@page` for margins, page size)
- Embeds fonts for consistent rendering
- Generates print-ready PDF with proper pagination

---

## Rendering Features

The script renders different element types with distinct visual treatments to make the manuscript readable and semantically meaningful.

### 1. Structural Elements

#### `<div>` - Text Division / Entry
**Purpose:** Logical sections of the manuscript (entries, recipes)
**Attributes:**
- `id`: Unique identifier (e.g., `p001r_1`)
- `categories`: Semantic tags (e.g., `lists;materials`)

**Rendering:**
- Wrapped in `<div class="entry">`
- Bottom margin for separation
- Avoids page breaks mid-entry
- Followed by margin notes section (if any)

#### `<head>` - Heading
**Purpose:** Entry titles and headings
**Rendering:**
- `<h3>` element. Two styles are applied based on the `margin` attribute:
  - **Major Heading:** 18pt, bold, dark gray, with a solid bottom border. This is the default.
  - **Minor Heading:** 14pt, bold, dark gray, with a lighter bottom border. Applied when the `margin` attribute contains 'left-middle' or 'right-top'.

#### `<ab>` - Anonymous Block
**Purpose:** Primary text container for manuscript content
**Attributes:**
- `margin`: Position in page margin (e.g., `left-middle`, `right-top`)
- `render`: Size hints (`wide`, `tall`)

**Rendering:**
- **Without `margin` attribute:** `<p>` paragraph, justified text
- **With `margin` attribute:** Extracted to margin notes section (see below)

#### `<hr>` - Horizontal Rule
**Rendering:** Thin gray line separator

#### `<lb>` - Line Break
**Rendering:** `<br/>` HTML line break

---

### 2. Semantic Elements

**Note:** The color-coded styling for these elements is optional. By default, they are rendered as plain text. To enable the styling described below, run the script with the `--semantic` flag.

These elements mark significant terms and concepts. Each receives distinct color-coding:

| Element | Meaning | Styling | Examples |
|---------|---------|---------|----------|
| `<pn>` | Personal Name | Bold, teal (#16a085) | Mestre Jehan Cousin, Bernard Palissi |
| `<pl>` | Place | Medium weight, blue (#2980b9) | Rue de la Heaumerie, Lyon |
| `<pro>` | Profession | Small caps, purple (#8e44ad) | master, harvester, currier |
| `<m>` | Material | Orange (#d35400) | sand, oil, wax |
| `<pa>` | Plant | Green (#27ae60) | pastel woad, oak |
| `<al>` | Animal | Red (#c0392b) | horse, falcon |
| `<tl>` | Tool | Gray (#7f8c8d) | mold, hammer |
| `<ms>` | Measurement | Monospace font | one pound, three fingers |
| `<env>` | Environment | Teal (#16a085) | workshop, mountains |
| `<tmp>` | Temporal | Italic, gray (#95a5a6) | hour, season, day |
| `<bp>` | Body Part | Red (#e74c3c) | hand, eye |
| `<cn>` | Currency | Gold (#f39c12) | franc, écu |
| `<mu>` | Musical Instrument | Purple (#9b59b6) | lute, trumpet |
| `<md>` | Medical | Orange (#e67e22) | plague, fever |
| `<wp>` | Weapon | Red (#c0392b) | sword, cannon |
| `<sn>` | Sense | Italic | smooth, shiny, fragrant |
| `<df>` | Definition | Medium weight | - |

**Rendering Details:**
- All rendered as `<span>` elements with class names
- CSS applies colors, weights, and typography
- Nested semantic elements are supported (e.g., `<m>` containing `<pa>`)

---

### 3. Language Elements

Mark text in languages other than English:

| Element | Language | Styling | Notes |
|---------|----------|---------|-------|
| `<la>` | Latin | Italic, dark gray | Most common |
| `<fr>` | French | Italic | - |
| `<it>` | Italian | Italic | - |
| `<de>` | German | Italic | - |
| `<el>` | Greek | Italic | - |
| `<oc>` | Occitan | Italic | - |
| `<po>` | Poitevin | Italic | Dialect |

**Purpose:** Distinguishes multilingual content in the Renaissance manuscript

---

### 4. Transcription Elements

Record editorial interventions and manuscript features:

| Element | Meaning | Rendering | Purpose |
|---------|---------|-----------|---------|
| `<emph>` | Emphasized | Italic (`<em>`) | Text emphasized in original |
| `<underline>` | Underlined | Underlined (`<u>`) | Underlined in original |
| `<sup>` / `<superscript>` | Superscript/Supplied | Superscript (`<sup>`) | Supplied or superscript text |
| `<del>` | Deletion | Strikethrough (`<del>`), gray | Deleted by author |
| `<add>` | Addition | Dotted underline (`<ins>`) | Added by author |
| `<exp>` | Expansion | Normal | Abbreviation expanded by editor |
| `<corr>` | Correction | Blue | Editor correction |
| `<ill>` | Illegible | Gray, italic, "[illegible]" | Unreadable in original |
| `<gap>` | Gap | Gray, italic, "[gap]" | Missing text |
| `<mark>` | Mark/Symbol | Bold, red | Special symbols |

**Purpose:** Preserves transcription fidelity and editorial transparency

---

### 5. Other Elements

#### `<comment>` - Comment Reference
**Rendering:** Small superscript in blue (e.g., `[c_001r_01]`)
**Purpose:** Links to editorial commentary (not included in PDF)

#### `<figure>` - Figure
**Rendering:** Gray box with figure description `[Figure: description]`
**Purpose:** Placeholder for manuscript images

---

## Margin Notes Extraction

### What are Margin Notes?

In the original manuscript, many entries include annotations written in the page margins (left, right, top, bottom). These marginal notes provide additional information, cross-references, or supplementary content.

### Extraction Process

1. **Detection:** During XML processing, when an `<ab>` element has a `margin` attribute, it's flagged as a margin note

2. **Collection:** Instead of rendering inline, the note is:
   - Converted to HTML
   - Added to a collection list for the current `<div>`
   - Position label added (e.g., `[left-middle]`)

3. **Placement:** After the `<div>` closes, all collected margin notes are rendered in a dedicated section:
   ```html
   <div class="margin-notes">
       <h3>Margin Notes:</h3>
       <div class="margin-note" data-position="left-middle">
           [left-middle] Note content here...
       </div>
       ...
   </div>
   ```

### Styling

Margin notes sections receive distinct visual treatment:
- Light gray background (#f8f9fa)
- Blue left border (4px, #3498db)
- Clear "Margin Notes:" header
- Individual notes have white background
- Position labels in small caps, gray
- Smaller font size (10pt vs 11pt main text)

### Purpose

This design choice:
- **Separates** marginal content from main text flow
- **Preserves** positional information (which margin)
- **Enhances** readability (no interruptions in main text)
- **Maintains** semantic meaning (notes remain associated with entries)

---

## Styling and Typography

### Page Layout

```css
@page {
    size: letter;          /* US Letter (8.5" × 11") */
    margin: 1in;           /* 1 inch margins all sides */
}
```

**Print-ready specifications:**
- Standard paper size for US printing
- Professional margin width
- Suitable for binding

### Typography

**Body Text:**
- **Font:** Garamond (primary), Georgia (fallback), Times New Roman (fallback), serif (generic)
- **Size:** 11pt
- **Line height:** 1.6 (comfortable reading)
- **Color:** Black (#000)

**Headings (Entry Titles):**
- **Size:** 14pt
- **Weight:** Bold
- **Color:** Dark gray (#2c3e50)
- **Border:** Bottom border for visual separation

**Margin Notes:**
- **Size:** 10pt (smaller than main text)
- **Line height:** 1.5

### Color Scheme

The script uses a carefully designed color palette:

**Semantic Categories:**
- **Teal/Cyan** (#16a085): People, environments
- **Blue** (#2980b9): Places
- **Purple** (#8e44ad, #9b59b6): Professions, music
- **Orange** (#d35400, #e67e22, #f39c12): Materials, medical, currency
- **Green** (#27ae60): Plants
- **Red** (#c0392b, #e74c3c): Animals, body parts, weapons
- **Gray** (#7f8c8d, #95a5a6): Tools, temporal, illegible text

**Design Principles:**
- Distinct hues for easy differentiation
- Muted saturation for print-friendliness
- Sufficient contrast for readability
- Consistent with academic/scholarly design

### Page Breaks

```css
.entry {
    page-break-inside: avoid;  /* Keep entries together */
}

.margin-notes {
    page-break-inside: avoid;  /* Keep notes with entry */
}
```

Prevents awkward splits in the middle of entries or notes.

---

## Dependencies and Setup

### System Requirements

**Python:** 3.8 or higher

### Python Dependencies

```
weasyprint>=67.0
```

Weasyprint provides HTML/CSS to PDF conversion with:
- Full CSS support (including @page rules)
- Font embedding
- Print-quality output
- SVG support

### System Libraries (for weasyprint)

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Ubuntu/Debian:**
```bash
apt-get install python3-pip python3-cffi python3-brotli \
                libpango-1.0-0 libpangoft2-1.0-0 \
                libcairo2 libgdk-pixbuf2.0-0
```

### Installation

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install Python dependencies
pip install weasyprint
```

---

## Usage

The script is run from the command line and accepts an optional flag to control semantic styling.

### Basic Usage

```bash
# From repository root
source .venv/bin/activate
python3 lib/generate_pdf.py
```
This will generate the PDF without any special coloring for semantic elements.

### Command-Line Options

#### `--semantic`
- **Purpose:** Enables the rendering of semantic elements with special styling (colors, font weights, etc.).
- **Default:** Off.
- **Usage:**
  ```bash
  python3 lib/generate_pdf.py --semantic
  ```

### Output

The script produces two files:
1.  **allFolios/pdf/all_tl.html**
    - An intermediate HTML file containing the manuscript content.
    - This file can be opened in a web browser for debugging or viewing.

2.  **allFolios/pdf/all_tl.pdf**
    - The final, print-ready PDF.
    - The content of this file depends on the `--semantic` flag. If the flag is used, the PDF will include color-coded semantic styling. Otherwise, it will be plain text.

---

## Extending the Script

### Adding Support for Other Versions

Currently supports: **tl** (English translation)

To add **tc** (French transcription) or **tcn** (normalized transcription):

```python
def main():
    # Configuration
    versions = {
        'tc': ('allFolios/xml/tc/all_tc.xml', 'BnF Ms. Fr. 640 - Transcription'),
        'tcn': ('allFolios/xml/tcn/all_tcn.xml', 'BnF Ms. Fr. 640 - Normalized'),
        'tl': ('allFolios/xml/tl/all_tl.xml', 'BnF Ms. Fr. 640 - Translation'),
    }

    # Process each version
    for version_code, (xml_path, title) in versions.items():
        # ... conversion logic
```

### Adding New Semantic Elements

1. **Add element handler** in `process_element()`:
```python
elif tag == "new_element":
    html = '<span class="new_element">'
    if text:
        html += escape_html(text)
    for child in elem:
        html += process_element(child, depth + 1)
    html += '</span>'
    if tail:
        html += escape_html(tail)
    return html
```

2. **Add CSS styling** in `get_css()`:
```css
.new_element {
    color: #hexcolor;
    font-weight: bold;
}
```

### Customizing Styling

Edit `get_css()` function to modify:
- **Colors:** Change hex values for semantic elements
- **Fonts:** Update font-family stacks
- **Sizes:** Adjust font-size, margins, padding
- **Layout:** Modify page size, margins

### Changing Output Location

Edit `main()` function:
```python
html_file = Path("custom/path/output.html")
pdf_file = Path("custom/path/output.pdf")
```

---

## Technical Notes

### XML Element Processing

The recursive `process_element()` function maintains:
- **Depth tracking:** For debugging nested structures
- **Margin notes context:** Passed down through recursion
- **Text preservation:** Both element text and tail text

### HTML Escaping

All text content is escaped to prevent:
- XSS vulnerabilities (though not applicable here)
- HTML rendering errors
- Special character issues

Characters escaped: `& < > " '`

### Memory Efficiency

The script:
- Parses XML lazily (ElementTree is memory-efficient)
- Builds HTML as strings (no DOM manipulation overhead)
- Writes output in single operation

For very large manuscripts, consider streaming approaches.

### Error Handling

The script handles:
- Missing input files (exits with error code 1)
- Missing weasyprint (falls back to HTML-only)
- XML parsing errors (ElementTree exceptions)
- File I/O errors

---

## File Statistics

**Input XML:** 988 KB, ~24,655 lines
**Output HTML:** 1.3 MB, ~25,000 lines
**Output PDF:** 3.2 MB, ~hundreds of pages

**Margin Notes:** 656 sections extracted

---

## Changelog

### Version 1.1 (Current)
- ✅ Added margin note extraction feature
- ✅ Comprehensive code comments
- ✅ Complete documentation
- ✅ Output to `allFolios/pdf/` directory

### Version 1.0 (Initial)
- ✅ Basic XML to HTML conversion
- ✅ Semantic element styling
- ✅ PDF generation with weasyprint

---

## References

- **Making and Knowing Project:** https://www.makingandknowing.org/
- **Digital Critical Edition:** https://edition640.makingandknowing.org/
- **Repository:** https://github.com/cu-mkp/m-k-manuscript-data
- **Weasyprint Documentation:** https://weasyprint.org/
- **BnF Ms. Fr. 640:** Bibliothèque nationale de France manuscript

---

## Support

For issues or questions:
1. Check this documentation
2. Review inline code comments
3. Open an issue on GitHub
4. Contact the Making and Knowing Project

---

*Generated for the Making and Knowing Project*
*Last Updated: 2024*
