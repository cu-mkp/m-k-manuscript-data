DIFF_MS_TXT_TC=$(comm -23 <(find ./ms-txt/tc -type f | sort) <(find ./ms-txt/tc -type f -name "tc_p[0-9][0-9][0-9][rv]_preTEI\.txt" | sort))
DIFF_MS_TXT_TCN=$(comm -23 <(find ./ms-txt/tcn -type f | sort) <(find ./ms-txt/tcn -type f -name "tcn_p[0-9][0-9][0-9][rv]_preTEI\.txt" | sort))
DIFF_MS_TXT_TL=$(comm -23 <(find ./ms-txt/tl -type f | sort) <(find ./ms-txt/tl -type f -name "tl_p[0-9][0-9][0-9][rv]_preTEI\.txt" | sort))

DIFF_ENTRIES_XML_TC=$(comm -23 <(find ./entries/xml/tc -type f | sort) <(find ./entries/xml/tc -type f -name "tc_p[0-9][0-9][0-9][rv]_[0-9]\.xml" | sort))
DIFF_ENTRIES_XML_TCN=$(comm -23 <(find ./entries/xml/tcn -type f | sort) <(find ./entries/xml/tcn -type f -name "tcn_p[0-9][0-9][0-9][rv]_[0-9]\.xml" | sort))
DIFF_ENTRIES_XML_TL=$(comm -23 <(find ./entries/xml/tl -type f | sort) <(find ./entries/xml/tl -type f -name "tl_p[0-9][0-9][0-9][rv]_[0-9]\.xml" | sort))
DIFF_ENTRIES_TXT_TC=$(comm -23 <(find ./entries/txt/tc -type f | sort) <(find ./entries/txt/tc -type f -name "tc_p[0-9][0-9][0-9][rv]_[0-9]\.txt" | sort))
DIFF_ENTRIES_TXT_TCN=$(comm -23 <(find ./entries/txt/tcn -type f | sort) <(find ./entries/txt/tcn -type f -name "tcn_p[0-9][0-9][0-9][rv]_[0-9]\.txt" | sort))
DIFF_ENTRIES_TXT_TL=$(comm -23 <(find ./entries/txt/tl -type f | sort) <(find ./entries/txt/tl -type f -name "tl_p[0-9][0-9][0-9][rv]_[0-9]\.txt" | sort))

DIFF_ALL_FOLIOS_XML_TC=$(comm -23 <(find ./allFolios/xml/tc -type f | sort) <(find ./allFolios/xml/tc -type f -name "all_tc\.xml" | sort))
DIFF_ALL_FOLIOS_XML_TCN=$(comm -23 <(find ./allFolios/xml/tcn -type f | sort) <(find ./allFolios/xml/tcn -type f -name "all_tcn\.xml" | sort))
DIFF_ALL_FOLIOS_XML_TL=$(comm -23 <(find ./allFolios/xml/tl -type f | sort) <(find ./allFolios/xml/tl -type f -name "all_tl\.xml" | sort))
DIFF_ALL_FOLIOS_TXT_TC=$(comm -23 <(find ./allFolios/txt/tc -type f | sort) <(find ./allFolios/txt/tc -type f -name "all_tc\.txt" | sort))
DIFF_ALL_FOLIOS_TXT_TCN=$(comm -23 <(find ./allFolios/txt/tcn -type f | sort) <(find ./allFolios/txt/tcn -type f -name "all_tcn\.txt" | sort))
DIFF_ALL_FOLIOS_TXT_TL=$(comm -23 <(find ./allFolios/txt/tl -type f | sort) <(find ./allFolios/txt/tl -type f -name "all_tl\.txt" | sort))

ERRCODE=0

if [ ! -z "$DIFF_MS_TXT_TC" ]
then
    echo "error: found files in ms-txt/tc not matching pattern:" >&2
    echo "$DIFF_MS_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_MS_TXT_TCN" ]
then
    echo "error: found files in ms-txt/tcn not matching pattern:" >&2
    echo "$DIFF_MS_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_MS_TXT_TL" ]
then
    echo "error: found files in ms-txt/tl not matching pattern:" >&2
    echo "$DIFF_MS_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_XML_TC" ]
then
    echo "error: found files in entries/xml/tc files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_XML_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_XML_TCN" ]
then
    echo "error: found files in entries/xml/tcn files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_XML_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_XML_TL" ]
then
    echo "error: found files in entries/xml/tl files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_XML_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_TXT_TC" ]
then
    echo "error: found files in entries/txt/tc files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_TXT_TCN" ]
then
    echo "error: found files in entries/txt/tcn files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ENTRIES_TXT_TL" ]
then
    echo "error: found files in entries/txt/tl files not matching pattern:" >&2
    echo "$DIFF_ENTRIES_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_XML_TC" ]
then
    echo "error: found files in allFolios/xml/tc file not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_XML_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_XML_TCN" ]
then
    echo "error: found files in allFolios/xml/tcn file not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_XML_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_XML_TL" ]
then
    echo "error: found files in allFolios/xml/tl file not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_XML_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_TXT_TC" ]
then
    echo "error: found files in allFolios/txt/tc files not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_TXT_TCN" ]
then
    echo "error: found files in allFolios/txt/tcn file not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ ! -z "$DIFF_ALL_FOLIOS_TXT_TL" ]
then
    echo "error: found files in allFolios/txt/tl file not matching pattern:" >&2
    echo "$DIFF_ALL_FOLIOS_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

exit $ERRCODE

