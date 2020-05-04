for F in *.txt;do BASENAME=${F%%.*}; cat $F | tr '[:upper:]' '[:lower:]' | tr -d '[:punct:]' | tr ' ' '\n'  | sort | uniq -c | sort -nr | tail +2  > "$BASENAME"_frq.txt ; done
