#! //bin/bash

ELEMENTS="al bp cn def env m md ms mu pa pl pn pro sn tl tmp"

rm term_usage/term_cnts.txt 

for ELEMENT in $ELEMENTS

do 
XPATH="//$ELEMENT"
echo $ELEMENT
# xml sel -t -m '//cn' -n  -v .  *.xml | sort | uniq -c | sort -nr
xml sel -t -m "$XPATH" -n -v 'normalize-space(.)' ms-xml/tc/*.xml | sort | uniq -c | sort -nr | tr -s ' ' ' ' | cut -d' ' -f 2- | sed 's/ /|/1' > vocabulary/term_usage/"$ELEMENT"_fq.csv 

wc -l vocabulary/term_usage/"$ELEMENT"_fq.csv >> vocabulary/term_usage/term_cnts.txt

done

