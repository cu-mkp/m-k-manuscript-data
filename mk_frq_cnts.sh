#! //bin/bash

ELEMENTS="al bp cn env m md ms mu pa pl pn pro sn tl tmp"

rm term_usage/term_cnts.txt 

for ELEMENT in $ELEMENTS

do 
XPATH="//$ELEMENT"
echo $ELEMENT
# xml sel -t -m '//cn' -n  -v .  *.xml | sort | uniq -c | sort -nr
xml sel -t -m "$XPATH" -n -v .  tc/*.xml | sort | uniq -c | sort -nr | awk '{ print $2 "," $1}' > term_usage/"$ELEMENT"_fq.csv 

wc -l term_usage/"$ELEMENT"_fq.csv >> term_usage/term_cnts.txt

done

