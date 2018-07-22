DOCX_DIR="/Users/terry/Github/making-knowing-assetserver/scripts/content_import/TEMP/input"

# wipe TEMP dir contents

rm -fr TEMP/*

# copy DOCX dir of rclone downloaded google drive folio files

cp -r $DOCX_DIR TEMP

# sanitize paths of copied docx files

detox -r TEMP

# Loop over each folio version type

for VERSION in tc tcn tl

do	       
# Loop over all downloaded DOCX files by version	       
    for DOCX_PATH in `find TEMP -name '*.txt' | grep "$VERSION"_ `
	    
    do
# Get basename of docx file
	FILE=`basename $DOCX_PATH`
# Get basename less file extension
	BASENAME="${FILE%%.*}"
	echo $BASENAME
# create root element start tag for xml of folio file
	echo "<root>" > "$VERSION"/"$BASENAME""_preTEI.xml"
# convert docx to plain text using pandoc, output as body of xml folio file
	#	pandoc -t plain -f docx "$DOCX_PATH" >> "$VERSION"/"$BASENAME""_preTEI.xml"

	cat "$DOCX_PATH" >> "$VERSION"/"$BASENAME""_preTEI.xml"
	
# append root close tag to xml folio file	
	echo "</root>" >> "$VERSION"/"$BASENAME""_preTEI.xml"
    done

done

