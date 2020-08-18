[![Build Status](https://travis-ci.org/cu-mkp/m-k-manuscript-data.svg?branch=master)](https://travis-ci.org/cu-mkp/m-k-manuscript-data)

Working files and data for the XML transcription and translation of Making and Knowing Project's Digital Critical Edition (DCE) of BnF Ms Fr 640. The repository contains the text of the manuscript in multiple formats, metadata about the manuscript, and derived data.

https://www.makingandknowing.org/

_Secrets of Craft and Nature in Renaissance France. A Digital Critical Edition and English Translation of BnF Ms. Fr. 640_
https://edition640.makingandknowing.org/


> Throughout: **tc** = transcription; **tcn** = normalized transcription **tl** = translation


## Directories

- allFolios - the individual manuscript folios as one continuous file, by version (tc, tcn, and tl)

- bibliogrpahy - bibliographic references in BibTex
 
- manuscript- object: https://github.com/cu-mkp/manuscript-object/tree/a8c8a712b555c9bbc0f0d3696e099a5da087e1e7

- metadata - data and additional information about the manuscript text and other materials of the DCE

- ms-md - each folio as an individual file (by version) in markdown

- ms-txt - each folio as an individual file (by version) in text

- ms-xml - each folio as an individual file (by version) in xml

- post_processed - manuscript text in alternative xml formats derived from ms-xml files  

- schema  - RelaxNG and Schematron schemas for project specific tag set

- vocabulary - listings of marked-up terms tagged in the manuscript 

- xslt - scripts used for processing xml



## Use in DCE

The following files and directories are watched for updates by the MK asset_server:

- metadata/annotation-metadata.csv
> --> https://edition640.makingandknowing.org/#/essays
- metadata/authors.csv
> --> https://edition640.makingandknowing.org/#/essays
- metadata/DCE_comment-tracking-Tracking.csv
> --> https://edition640.makingandknowing.org/#/folios
- metadata/entry_metadata.csv
> --> https://edition640.makingandknowing.org/#/entries
- glossary/DCE-glossary-table.csv
> --> https://edition640.makingandknowing.org/#/folios/1r/f/1r/glossary
- ms-xml/*
> --> https://edition640.makingandknowing.org/#/folios

Modification of these files on the master branch results in changes on the staging server.



