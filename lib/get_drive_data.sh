INFOLDER="TEMP/input"

USER=terry
GOOGLE_SHARE_NAME=BnF\ Ms\ Fr\ 640/__Manuscript\ Pages
RCLONE_SOURCE_NAME=google
RCLONE_CONFIG_FILE=/Users/$USER/.config/rclone/rclone.conf


# rm INFOLDER dir contents

# rm -fr TEMP/*


# do rclone sync from Google Drive

# rclone --drive-formats docx --include *.docx --config="$RCLONE_CONFIG_FILE" -v --fast-list --drive-shared-with-me sync "$RCLONE_SOURCE_NAME":"$GOOGLE_SHARE_NAME" "$INFOLDER"

# sanitize paths of copied docx files

# detox -r TEMP

# Loop over each folio version type

for VERSION in tc tcn tl

do	       
# Loop over all downloaded DOCX files by version
    for DOCX_PATH in `find TEMP -name '*.docx' | grep "$VERSION"_ `
	    
    do
# Get basename of docx file
	FILE=`basename $DOCX_PATH`
	echo "$FILE"
# Get basename less file extension
	BASENAME="${FILE%%.*}"
	echo $BASENAME
# create root element start tag for xml of folio file
	echo "<root>" > ms-xml/"$VERSION"/"$BASENAME""_preTEI.xml"
# convert docx to plain text using pandoc, output as body of xml folio file
      	pandoc -t plain -f docx "$DOCX_PATH" >> ms-xml/"$VERSION"/"$BASENAME""_preTEI.xml"

	
# append root close tag to xml folio file	
	echo "</root>" >> ms-xml/"$VERSION"/"$BASENAME""_preTEI.xml"
    done

done

