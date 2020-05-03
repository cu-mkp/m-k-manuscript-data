<?xml version="1.0" encoding="UTF-8" ?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:output method="text"/>
    <xsl:template match="/">
        <xsl:apply-templates select="//wp"/>
    </xsl:template>
    
    <xsl:template match="wp">
        <xsl:variable name="term" select="normalize-space(.)"/>
        
        <xsl:variable name="tok-before" select="tokenize(normalize-space(string-join(preceding::text(),'')),' ')"/>
        <xsl:variable name="tok-after" select="tokenize(normalize-space(string-join(following::text(),'')),' ')"/>
        <xsl:value-of select="$term"/><xsl:text>: </xsl:text>
        <xsl:value-of select="normalize-space(string-join(subsequence($tok-before,count($tok-before) -9), ' '))"/>
        <xsl:value-of select="concat(' ',$term,' ')"/>
        <xsl:value-of select="normalize-space(string-join(subsequence($tok-after,1,10), ' '))"/>
        <xsl:text>&#x0a;</xsl:text>
    </xsl:template>
    
    <xsl:template match="text()"/>
    
</xsl:transform>