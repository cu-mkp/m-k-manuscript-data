# within m-k-manuscript-data, create txt files of element counts for each version of text, housed in qc directory
# tl element counts
echo "generating tl element counts"
for XML in `find ../ms-xml/tl -name '*.xml'`
	do
		echo $XML
		xmlstarlet el "$XML" | rev | cut -d'/' -f1 | rev | sort | uniq -c
done
# > ../qc/elements-tl.txt
# tc element counts
# echo "generating tc element counts"
# for XML in `find ../ms-xml/tc -name '*.xml'` ;do echo $XML; xmlstarlet el "$XML" | rev | cut -d'/' -f1 | rev | sort | uniq -c ; done > ../qc/elements-tc.txt
#tcn element counts
# echo "generating tcn element counts"
# for XML in `find ../ms-xml/tcn -name '*.xml'` ;do echo $XML; xmlstarlet el "$XML" | rev | cut -d'/' -f1 | rev | sort | uniq -c ; done > ../qc/elements-tcn.txt
# echo "complete"