NUM_MS_TXT_TC=$(find ./ms-txt/tc -name *.txt | wc -l)
NUM_MS_TXT_TCN=$(find ./ms-txt/tcn -name *.txt | wc -l)
NUM_MS_TXT_TL=$(find ./ms-txt/tl -name *.txt | wc -l)

NUM_ENTRIES_XML_TC=$(find ./entries/xml/tc -name *.xml | wc -l)
NUM_ENTRIES_XML_TCN=$(find ./entries/xml/tcn -name *.xml | wc -l)
NUM_ENTRIES_XML_TL=$(find ./entries/xml/tl -name *.xml | wc -l)
NUM_ENTRIES_TXT_TC=$(find ./entries/txt/tc -name *.txt | wc -l)
NUM_ENTRIES_TXT_TCN=$(find ./entries/txt/tcn -name *.txt | wc -l)
NUM_ENTRIES_TXT_TL=$(find ./entries/txt/tl -name *.txt | wc -l)

NUM_ALL_FOLIOS_XML_TC=$(find ./allFolios/xml/tc -name *.xml | wc -l)
NUM_ALL_FOLIOS_XML_TCN=$(find ./allFolios/xml/tcn -name *.xml | wc -l)
NUM_ALL_FOLIOS_XML_TL=$(find ./allFolios/xml/tl -name *.xml | wc -l)
NUM_ALL_FOLIOS_TXT_TC=$(find ./allFolios/txt/tc -name *.txt | wc -l)
NUM_ALL_FOLIOS_TXT_TCN=$(find ./allFolios/txt/tcn -name *.txt | wc -l)
NUM_ALL_FOLIOS_TXT_TL=$(find ./allFolios/txt/tl -name *.txt | wc -l)

ERRCODE=0

if [ $NUM_MS_TXT_TC != 340 ]
then
    echo "error: expected 340 ms-txt/tc files; found $NUM_MS_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_MS_TXT_TCN != 340 ]
then
    echo "error: expected 340 ms-txt/tcn files; found $NUM_MS_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_MS_TXT_TL != 340 ]
then
    echo "error: expected 340 ms-txt/tl files; found $NUM_MS_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_XML_TC != 928 ]
then
    echo "error: expected 928 entries/xml/tc files; found $NUM_ENTRIES_XML_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_XML_TCN != 928 ]
then
    echo "error: expected 928 entries/xml/tcn files; found $NUM_ENTRIES_XML_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_XML_TL != 928 ]
then
    echo "error: expected 928 entries/xml/tl files; found $NUM_ENTRIES_XML_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_TXT_TC != 928 ]
then
    echo "error: expected 928 entries/txt/tc files; found $NUM_ENTRIES_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_TXT_TCN != 928 ]
then
    echo "error: expected 928 entries/txt/tcn files; found $NUM_ENTRIES_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ENTRIES_TXT_TL != 928 ]
then
    echo "error: expected 928 entries/txt/tl files; found $NUM_ENTRIES_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_XML_TC != 1 ]
then
    echo "error: expected 1 allFolios/xml/tc file; found $NUM_ALL_FOLIOS_XML_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_XML_TCN != 1 ]
then
    echo "error: expected 1 allFolios/xml/tcn file; found $NUM_ALL_FOLIOS_XML_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_XML_TL != 1 ]
then
    echo "error: expected 1 allFolios/xml/tl file; found $NUM_ALL_FOLIOS_XML_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_TXT_TC != 1 ]
then
    echo "error: expected 1 allFolios/txt/tc files; found $NUM_ALL_FOLIOS_TXT_TC" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_TXT_TCN != 1 ]
then
    echo "error: expected 1 allFolios/txt/tcn file; found $NUM_ALL_FOLIOS_TXT_TCN" >&2
    ERRCODE=$((ERRCODE+2))
fi

if [ $NUM_ALL_FOLIOS_TXT_TL != 1 ]
then
    echo "error: expected 1 allFolios/txt/tl file; found $NUM_ALL_FOLIOS_TXT_TL" >&2
    ERRCODE=$((ERRCODE+2))
fi

exit $ERRCODE
