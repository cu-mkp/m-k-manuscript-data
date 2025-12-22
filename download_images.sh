#!/bin/bash

# Create the images directory if it doesn't exist
mkdir -p images

# Read the CSV file and download the images
while IFS=, read -r folio div_id heading_tc heading_tcn heading_tl category add_cat_1 add_cat_2; do
    # Skip the header row
    if [[ "$folio" == "folio" ]]; then
        continue
    fi

    # Construct the image URL
    base_url="https://edition-assets.makingandknowing.org/manuscript-figures/"
    img_filename=$(echo "$div_id" | sed 's/fig_//')
    img_url="${base_url}${img_filename}.png"

    # Construct the local image path
    local_img_path="images/${img_filename}.png"

    # Download the image if it doesn't exist
    if [ ! -f "$local_img_path" ]; then
        echo "Downloading $img_url to $local_img_path"
        curl -A "Mozilla/5.0" -L "$img_url" -o "$local_img_path"
    fi
done < metadata/DCE_entry-category-metadata.csv
