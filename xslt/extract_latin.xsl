<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:output encoding="UTF-8" method="text"/>
    <xsl:template match="//la" name="it">
        <xsl:value-of select="normalize-space(.)"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="preceding::page[1]"/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
</xsl:stylesheet>