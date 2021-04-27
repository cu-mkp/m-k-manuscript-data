[![DOI](https://zenodo.org/badge/94773520.svg)](https://zenodo.org/badge/latestdoi/94773520)

![run-ci](https://github.com/cu-mkp/m-k-manuscript-data/workflows/run-ci/badge.svg)

Working files and data for the XML transcription and translation of Making and Knowing Project's Digital Critical Edition (DCE) of BnF Ms Fr 640. The repository contains the text of the manuscript in multiple formats, metadata about the manuscript, and derived data.

https://www.makingandknowing.org/

_Secrets of Craft and Nature in Renaissance France. A Digital Critical Edition and English Translation of BnF Ms. Fr. 640_
https://edition640.makingandknowing.org/


> Throughout: **tc** = transcription; **tcn** = normalized transcription **tl** = translation


## Directories

- **allFolios** - the individual manuscript folios as one continuous file, by version (tc, tcn, and tl)

- **bibliogrpahies** - bibliographic references in BibTex, used in [bibliography.md](https://github.com/cu-mkp/edition-webpages/blob/master/docs/resources/bibliography.md) for the DCE's [Bibliography](https://edition640.makingandknowing.org/#/content/resources/bibliography). These are grouped into references used in the DCE's [glossary](https://github.com/cu-mkp/m-k-manuscript-data/blob/master/glossary/DCE-glossary-table.csv) and the [editorial comments](https://github.com/cu-mkp/m-k-manuscript-data/blob/master/metadata/DCE_comment-tracking-Tracking.csv)

- **entries** - for each version of the text, every entry as a single file in both XML and TXT formats, derived from ms-xml/

- **glossary** - a record of distinctive terms used in the manuscript and a translation aid for Middle French terms and Renaissance workshop materials, compiled during the process of transcribing and translating Ms. Fr. 640

- **lib** - scripts used for maintenance of repository

- **metadata** - data and additional information about the manuscript text and other materials of the DCE

- **ms-md** - each folio as an individual file (by version) in markdown format, derived from ms-xml/ and used in the [Minimal Edition of BnF Ms. Fr. 640 (Workshop Version)](https://cu-mkp.github.io/2017-workshop-edition/). See also [cu-mkp/2017-workshop-edition](https://github.com/cu-mkp/2017-workshop-edition)

- **ms-txt** - each folio as an individual file (by version) in text format, derived from ms-xml/

- **ms-xml** - each folio as an individual file (by version) in xml format, derived from ms-xml/

- **qc** - listings and counts to aid in the process of ms-xml markup consistency and accuracy

- **reference_docs** - records of special characters and unicode symbols used in ms-xml other than the standard printing (US-layout keyboard) characters

- **schema** - RelaxNG and Schematron schemas for project specific tag set

- **vocabulary** - listings of marked-up terms tagged in the manuscript 

- **xslt** - scripts used for processing xml
  
## Use in DCE

The following files and directories are watched for updates by the MK asset_server:

- metadata/annotation-metadata.csv --> https://edition640.makingandknowing.org/#/essays
- metadata/authors.csv --> https://edition640.makingandknowing.org/#/essays
- metadata/DCE_comment-tracking-Tracking.csv --> https://edition640.makingandknowing.org/#/folios
- metadata/entry_metadata.csv --> https://edition640.makingandknowing.org/#/entries
- glossary/DCE-glossary-table.csv --> https://edition640.makingandknowing.org/#/folios/1r/f/1r/glossary
- ms-xml/* --> https://edition640.makingandknowing.org/#/folios

Modification of these files on the master branch results in changes on the staging/development server.


## Derivative Files

A number of files are generated from ms-xml/ by **[manuscript-object](https://github.com/cu-mkp/manuscript-object)**. 

These include:
- allFolios/: for each version, a single XML file containing each folio concatenated together
- entries/: for each version, every entry as a single file in both XML and TXT formats
- metadata/entry_metadata.csv: listing of the properties of each entry, including IDs, headings, and semantic tags (the significant properties of the manuscript as defined by the M&K Project editors), and is used to generate the [List of Entries](https://edition640.makingandknowing.org/#/entries)
- ms-txt/: for each version, every folio as a single file in TXT format. 

**NOTE for TXT versions:** 
- UTF-8 encoding
- ampersand (&) is rendered in its literal form rather than the character entity `&amp`
- if text is marked in ms-xml/ as `<add>` (additions), `<corr>` (corrections), `<del>` (deletions), `<exp>` (expansions), and `<sup>` (supplied), the text is retained and unmarked
- figures and comments are absent and unmarked

**Making changes to derivative files in `m-k-manuscript-data`:**

1. `cd` to `m-k-manuscript-data` directory
2. `git fetch`
3. `git pull`
4. Checkout a branch: `git checkout -b [name of branch]`
5. `cd` to `manuscript-object` directory
6. `git fetch`
7. `git pull`
8. Run update.py: `python3 update.py` (might need to use `python3.8`, e.g., if you have more than one version installed)
9. `cd` back to `m-k-manuscript-data` directory
10. `git add .`
11. `git commit -m '#[issue##]: [commit message]'`
12. `git push -u origin [name of branch]`
