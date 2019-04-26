
* check for well formedness
 * using xmlstarlet:
  *  xml val -w -g ms-xml/*/*.xml
 * using xmllint:
  *  xmllint --noout ms-xml/*/*.xml
 * correct any errors before proceeding
* generate single file xml for each version
 * run mk_single_file.xsl for with param “mode=[tc|tcn|tl]" and initial template (-it) “it"
* generate text versions of allFolios xml
 * run strip_tags.xsl for each file in allFolios/xml/, outputting to corresponding file in allFolios/txt/
* generate text versions of folio xml files
 * run strip_tags.xsl for each file in ms-xml/xml/[tc|tcn|tl], outputting to corresponding file in ms-txt/[tc|tcn|tl]
* generate tag usage reports
 *  xml el all_tl.xml | rev | cut -d'/' -f1 | rev | sort | uniq -c | rev | awk '{print $2, $1}' | rev | sort -k 2nr
* generate entry metadata based on allFolios/xml/all_tc.xml
 * output to metadata/entry_metadata.tsv
* generate div metadata based on allFolios/xml/all_tc.xml
 * output to metadata/figure_data.tsv

Other notes:
use paste to compare lines across files
 *  paste -d'|' ../ms-txt/tc/tc_p109r_preTEI.txt ../ms-txt/tcn/tcn_p109r_preTEI.txt
