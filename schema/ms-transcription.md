
start =

 ## Root element for transcription of folio
  ```
  element root {
    mixed {
      element page { xsd:NMTOKEN },
      element image { xsd:anyURI },
       (e.ab | e.figure | e.div)+
    }
  }

  ```

# BLOCK ELEMENTS

## ab

### Anonymous Block: a generic block of text
```
e.ab = element ab { e.cont?, e.margin?, m.phrase, e.cont? }
```
## div

### Text Division: A group of one or more document objects forming a primary textual component; e.g., an "entry" or "recipe"
```
e.div =
  element div {
    e.cont?,
    e.id,
    e.margin?,
    e.head?,
    (text | e.ab | m.phrase)+,
    e.cont?
  }
  ```
# figure

## Figure: a graphical object in the source document
```
e.figure =
  element figure {
    e.id?,
    e.margin?,
    element link { xsd:anyURI }?,
    (m.phrase
     | element caption { (text | m.phrase)+ })+
  }
  ```
# head

## Heading: a block of text at the beginning of a textual division functioning as the heading or title of that division. TEI Element
```
e.head = element head { m.phrase }

```

# TRANSCRIPTION ELEMENTS

## Addition: Text added to the document by author, scribe, but *not* by the editor or transcriber

```
e.add = element add { m.phrase }

```
# corr

## Correction: A revision introduced into the transcription by the editor or transcriber
```
e.corr = element corr { m.phrase }

```
# del

## Deletion: Content deleted in the document by author, scribe, but *not* by the editor or transcriber
```
e.del = element del { m.phrase }

```
# exp

## Expansion: text added by the editor or transcriber expanding an abbreviation in the source

```
e.exp = element exp { m.phrase }

```
# gap

## Gap: Text added to the document by author, scribe, but *not* by the editor or transcriber"

```
e.gap = element gap { empty }

```

# ill

## Illegible: unreadable text in the source document

```
e.ill = element ill { m.phrase }
```
# lb

## Line Break: An empty element indicating end of a line of text in the source document
```
e.lb = element lb { empty }
```
# man

## Manchette: a word or phrase in italic script in the margin that indicates something in the text block It is not a heading (although sometimes it looks like it, but rather explains something in the text block
```
e.man = element man { e.margin, m.phrase }
```
# rub

## Rubric: A word or phrase in italic script in the body of the text that is not a new div, heading, or block
```
e.rub = element rub { m.phrase }
```
# sup

## Supplied Text: Text added by the transcriber/editor.
```
e.sup = element sup { m.phrase }
```
# unc

## Unclear: Text which has been transcribed but with some uncertainty
```
e.unc = element unc { m.phrase }
```

# underline
```
e.underline = element underline { m.phrase }
```
# exp

## X: used to indicate ambiguous use of square brackets in the transcription
```
e.x = element x { m.phrase }

```
#

# ATTR-LIKE ELEMENTS

## Identifier: A unique identifier for the element which encloses
```
e.id = element id { xsd:NMTOKEN }
```

# margin

## Margin Position: the location in the margin at which the parent element appears in the source document. Valid values are: "right-top", "right-middle", "right-bottom", "left-top", "left-middle", "left-bottom", "top", and "bottom"
```
e.margin =
  element margin {
    ("left-top"
     | "left-middle"
     | "left-bottom"
     | "right-top"
     | "right-middle"
     | "right-bottom"
     | "top"
     | "bottom")?
  }
```
## Continued: An empty element indicating that the parent block is continued on another page or continues from another page
```
e.cont = element cont { empty }
```

# LANGUAGE ELEMENTS

# gk

## Greek: Greek text
```
e.gk = element gk { m.phrase }
```
# it

## Italian: Italian text
```
e.it = element it { m.phrase }
```
# la

## Latin: Latin text
```
e.la = element la { m.phrase }
```
# fr

## French: French text
```
e.fr = element fr { m.phrase }
```
# oc

## Occitane: Occitane text
```
e.oc = element oc { m.phrase }
```

# SEMANTIC ELEMENTS

# bp

## Body Part
```
e.bp = element bp { m.phrase }
```
# pro

## Profession
```
e.pro = element pro { m.phrase }
```
# ms

## Measurement
```
e.ms = element ms { m.phrase }
```
# al

## Animal
```e.al = element al { m.phrase }
```
# env

## Environment: Reference to a physical space or environment, such as workshop space, mountains, forest, etc.
```
e.env = element env { m.phrase }
```
# m

## Material
```e.m = element m { m.phrase }
```
# pa

## Plant
```e.pa = element pa { m.phrase }
```
# tmp

## Temporal Term: A reference to time, e.g., hour, day, season, holiday, span of time, time of day, etc
```e.tmp = element tmp { m.phrase }
```
# tl

## Tool
```
e.tl = element tl { m.phrase }
```
# sn

## Sense Term: Use of the 5 senses to make qualitative assessment, but generally not visual, e.g., “luisant”
```
e.sn = element sn { m.phrase }
```
# pl

## Place Term
```
e.pl = element pl { m.phrase }
```
# pn

## Personal Name
```
e.pn = element pn { m.phrase }
```
# cn

## Currency Term: Coins and currency (only type of coin, not amount)
```
e.cn = element cn { m.phrase }
```
# mu

## Musical Instrument
```
e.mu = element mu { m.phrase }
```
# md

## Medical Term: medical and health-related terms or phrases, such as disease terms, as plague and mange, or medical advice, if possible
```
e.md = element md { m.phrase }
```
# PHRASE MODEL

# m.phrase
```
m.phrase =
  (text
   | e.ab
   | e.add
   | e.al
   | e.bp
   | e.cn
   | e.del
   | e.env
   | e.figure
   | e.fr
   | e.it
   | e.ill
   | e.la
   | e.lb
   | e.m
   | e.man
   | e.ms
   | e.pa
   | e.pl
   | e.pn
   | e.pro
   | e.sn
   | e.sup
   | e.tl
   | e.tmp
   | e.corr
   | e.gap
   | e.gk
   | e.md
   | e.mu
   | e.oc
   | e.rub
   | e.underline
   | e.exp
   | e.x
   | e.unc)+
```
