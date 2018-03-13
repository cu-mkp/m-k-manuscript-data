DOCX_DIR="/Users/terry/Github/making-knowing-assetserver/scripts/content_import/TEMP/input"

rm -fr TEMP/*

cp -r $DOCX_DIR TEMP

detox -r TEMP

for VERSION in tc tcn tl

do	       
	       
    for DOCX_PATH in `find TEMP -name '*.docx' | grep "$VERSION"_ `
	    
    do

	FILE=`basename $DOCX_PATH`
	BASENAME="${FILE%%.*}"
	echo $BASENAME
	echo "<root>" > "$VERSION"/"$BASENAME""_preTEI.xml"
	pandoc -t plain -f docx "$DOCX_PATH" >> "$VERSION"/"$BASENAME""_preTEI.xml"
	echo "</root>" >> "$VERSION"/"$BASENAME""_preTEI.xml"
    done

done

