default namespace = ""
namespace a = "http://relaxng.org/ns/compatibility/annotations/1.0"
namespace s = "http://www.ascc.net/xml/schematron"

start =
  
  ## Root element for transcription of folio
  element root {
    mixed {
      element page { xsd:NMTOKEN },
      element image { xsd:anyURI },
      (# <text/>
       e.ab
       | e.figure
       | e.mark
       | e.div
       | e.hr)+
    }
  }
#

# BLOCK ELEMENTS

#

# ab

## Anonymous Block: a generic block of text
e.ab = element ab { e.cont?, e.margin?, e.render?, m.phrase, e.cont? }
# div

## Text Division: A group of one or more document objects forming a primary textual component; e.g., an "entry" or "recipe"
e.div =
  [
    s:pattern [
      name = "div-id"
      "\x{a}" ~
      "      "
      s:rule [
        context = "div"
        "\x{a}" ~
        "        "
        s:assert [
          test = "child::id"
          " \x{a}" ~
          "         Warning: div without an id"
        ]
        "\x{a}" ~
        "      "
      ]
      "\x{a}" ~
      "      "
    ]
  ]
  element div {
    e.cont?,
    e.id?,
    e.margin?,
    e.head?,
    (text | e.ab | e.figure | m.phrase)+,
    e.cont?
  }
# figure

## Figure: a graphical object in the source document
e.figure =
  element figure {
    e.id?,
    e.margin?,
    e.render?,
    element link { xsd:anyURI }?,
    (m.phrase
     | element caption { (text | m.phrase)+ })+
  }
# mark

## Mark: a symbol in the source text represented in the transcription by a utf-8 character
e.mark = element mark { xsd:string }
# head

## Heading: a block of text at the beginning of a textual division functioning as the heading or title of that division. TEI Element
e.head = element head { e.margin?, m.phrase }

## Horizontal rule
e.hr = element hr { empty }
#

# TRANSCRIPTION ELEMENTS

#

## Addition: Text added to the document by author, scribe, but *not* by the editor or transcriber
e.add = element add { m.phrase }
# corr

## Correction: A revision introduced into the transcription by the editor or transcriber
e.corr = element corr { m.phrase }
# del

## Deletion: Content deleted in the document by author, scribe, but *not* by the editor or transcriber
e.del = element del { m.phrase }
# exp

## Expansion: text added by the editor or transcriber expanding an abbreviation in the source
e.exp = element exp { m.phrase }
# gap

a:documentation [
  "Gap: Text added to the document by author, scribe, but *not* by the editor or transcriber"
]
e.gap = element gap { empty }
# ill

## Illegible: unreadable text in the source document
e.ill = element ill { m.phrase }
# lb

## Line Break: An empty element indicating end of a line of text in the source document
e.lb = element lb { empty }
# sup

## Supplied Text: Text added by the transcriber/editor.
e.sup = element sup { m.phrase }
# unc

## Unclear: Text which has been transcribed but with some uncertainty
e.unc = element unc { m.phrase }
# underline

## Underlined: underlined text
e.underline = element underline { m.phrase }
# emph

## Emph: emphasized text
e.emph = element emph { m.phrase }
# superscript

## superscript: superscript text
e.superscript = element superscript { m.phrase }
# ups

## ups: text under paper strip
e.ups = element ups { m.phrase }
#

# ATTR-LIKE ELEMENTS

#

# id

## Identifier: A unique identifier for its parent element 
e.id = element id { xsd:NMTOKEN }
# margin

## Margin (position): the location in the margin at which the parent element appears in the source document. Valid values are: "right-top", "right-middle", "right-bottom", "left-top", "left-middle", "left-bottom", "top", and "bottom"
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
# render

## Margin rendition: Instructions to cue the proper rendition of the height and width  a margin block. Valid values are: "tall", "wide", and "extra-wide"
e.render = element render { ("tall" | "wide" | "extra-wide")? }
# cont

## cont (continues): An empty element indicating that the parent block is continued on another page or continues from another page 
e.cont = element cont { empty }
#

# LANGUAGE ELEMENTS

#

# de

## German: German text
e.de = element de { m.phrase }
# el

## Greek: Greek text
e.el = element el { m.phrase }
# es

## Spanish: Spanish text
e.es = element es { m.phrase }
# fr

## French: French text
e.fr = element fr { m.phrase }
# it

## Italian: Italian text
e.it = element it { m.phrase }
# la

## Latin: Latin text
e.la = element la { m.phrase }
# oc

## Occitane: Occitane text
e.oc = element oc { m.phrase }
# po

## Poitevin: Poitevin dialect text
e.po = element po { m.phrase }
#

# SEMANTIC ELEMENTS

#

# al

## Animal
e.al = element al { m.phrase }
# bp

## Body Part
e.bp = element bp { m.phrase }
# pro

## Profession
e.pro = element pro { m.phrase }
# ms

## Measurement
e.ms = element ms { m.phrase }
# env

## Environment: Reference to a physical space or environment, such as workshop space, mountains, forest, etc.
e.env = element env { m.phrase }
# m

## Material
e.m = element m { m.phrase }
# pa

## Plant
e.pa = element pa { m.phrase }
# tmp

## Temporal Term: A reference to time, e.g., hour, day, season, holiday, span of time, time of day, etc
e.tmp = element tmp { m.phrase }
# tl

## Tool
e.tl = element tl { m.phrase }
# sn

## Sense Term: Use of the 5 senses to make qualitative assessment, but generally not visual, e.g., “luisant” 
e.sn = element sn { m.phrase }
# pl

## Place Term
e.pl = element pl { m.phrase }
# pn

## Personal Name
e.pn = element pn { m.phrase }
# cn

## Currency Term: Coins and currency (only type of coin, not amount)
e.cn = element cn { m.phrase }
# mu

## Musical Instrument
e.mu = element mu { m.phrase }
# md

## Medical Term: medical and health-related terms or phrases, such as disease terms, as plague and mange, or medical advice, if possible
e.md = element md { m.phrase }
# wp

## Weapon term: terms related to weapons and weaponry
e.wp = element wp { m.phrase }
# df

## Definition:
e.df = element df { m.phrase }
# comment
e.comment = element comment { xsd:string }
# PHRASE MODEL

# m.phrase
m.phrase =
  (text
   | e.ab
   | e.add
   | e.al
   | e.bp
   | e.cn
   | e.del
   | e.df
   | e.env
   | e.figure
   | e.mark
   | e.fr
   | e.it
   | e.ill
   | e.la
   | e.lb
   | e.m
   | e.ms
   | e.pa
   | e.pl
   | e.pn
   | e.pro
   | e.sn
   | e.sup
   | e.tl
   | e.tmp
   | e.wp
   | e.corr
   | e.gap
   | e.el
   | e.md
   | e.mu
   | e.oc
   | e.po
   | e.de
   | e.es
   | e.underline
   | e.superscript
   | e.exp
   | e.unc
   | e.comment
   | e.hr
   | e.emph
   | e.ups)+
