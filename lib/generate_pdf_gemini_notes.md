# Notes on the Critical Edition and PDF Generation

This document outlines the plan for improving the critical edition of the BnF Ms. Fr. 640, the changes implemented in the `generate_pdf_gemini.py` script, and instructions on how to use it.

## 1. Plan for the Critical Edition

To transform the current PDF into a more effective and scholarly critical edition, the following enhancements are recommended:

*   **Page Layout and Notes**:
    *   **Footnotes**: Replace the current endnote system with footnotes for immediate access to annotations.
    *   **Margin Notes**: Place marginalia in the actual page margins, aligned with the corresponding text, to replicate the manuscript layout.
    *   **Facing-Page Layout**: For a comprehensive scholarly edition, present the original French text on the left-hand page (verso) and the English translation on the right-hand page (recto).

*   **Critical Apparatus**:
    *   **Line Numbering**: Add line numbers to the main text for precise citation.
    *   **Standardized Apparatus**: Use the footnote space for a formal *apparatus criticus* to note textual variants, paleographic details, and other scholarly annotations.

*   **Textual and Visual Presentation**:
    *   **Typography**: Use distinct fonts to differentiate the main text, translated text, and editorial commentary.
    *   **Figures**: Replace placeholders like `[Figure: ...]` with the actual images from the manuscript.

*   **Standard Academic Sections**:
    *   **Introduction**: A detailed introduction covering the manuscript's history, editorial methods, and context.
    *   **Indices**: An `Index Nominum` (index of names) and `Index Rerum` (index of subjects) to make the edition a useful reference tool.
    *   **Bibliography**: A bibliography of all cited works.

## 2. Changes Implemented in `generate_pdf_gemini.py`

Based on user feedback, the following changes have been implemented in the `generate_pdf_gemini.py` script to improve the formatting of the generated PDF:

*   **Hybrid Note System**: To address the issue of footnote clutter at the beginning of the document, a hybrid system has been implemented:
    *   **Endnotes**: For the initial lists of names and authors, citations are rendered as endnotes at the end of the document.
    *   **Footnotes**: For the main body of the text (starting from the entry with ID `p001v_1`), all comments are rendered as footnotes at the bottom of the corresponding page.

*   **Margin Note Layout**: The two-column layout for margin notes has been reverted to the original, more robust block display. Margin notes now appear in a shaded block immediately following the entry they belong to. To prevent formatting issues with long notes, individual margin notes are styled to avoid breaking across pages.

*   **Heading Styles**: The script now distinguishes between major and minor headings.
    *   **Major Headings**: Main entry titles are rendered with a large font size and a prominent border.
    *   **Minor Headings**: Headings for lists and other preliminary materials are rendered with a smaller font size and a less prominent border to reduce their visual weight.

*   **File Paths and Naming**:
    *   The script has been moved to the `lib/` directory.
    *   Internal file paths have been updated to reflect the new location.
    *   The output PDF is now named `all_tl_gemini.pdf` to distinguish it from the original.

## 3. The `generate_pdf_gemini.py` Script

*   **Purpose**: This script converts the XML-encoded English translation of the BnF Ms. Fr. 640 into a styled, print-ready PDF.
*   **Input**:
    *   `../allFolios/xml/tl/all_tl.xml`: The XML source file for the English translation.
    *   `../metadata/DCE_comment-tracking-Tracking.csv`: A CSV file containing the content of the editorial comments.
*   **Output**:
    *   `../allFolios/pdf/all_tl.html`: An intermediate HTML file with all the content and styling.
    *   `../allFolios/pdf/all_tl_gemini.pdf`: The final, formatted PDF document.

## 4. How to Run the Script

To generate the PDF, follow these steps:

1.  **Navigate to the `lib` directory**:
    ```bash
    cd ../../lib
    ```

2.  **Activate the virtual environment and run the script**:
    ```bash
    source ../.venv/bin/activate && python3 generate_pdf_gemini.py
    ```

This will execute the script, which will parse the XML, generate the HTML, and then create the final PDF in the `allFolios/pdf` directory.
