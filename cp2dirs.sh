#! /bin/bash

DOWNLOAD_DIR="/Users/terry/Github/manuscript-pages/manuscript_downloads"
REPO_DIR="/Users/terry/Github/ms_xml"
TYPES="tc tcn tl"

for TYPE in $TYPES

do

echo $TYPE
rm "$REPO_DIR"/"$TYPE"/*.xml   
    
    for FILE in $(find "$DOWNLOAD_DIR" -name '*.xml' | grep "$TYPE""_")

        do

        echo "$FILE"
        
        cp "$FILE" "$TYPE"

        done

done