<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="#all" >
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    <xsl:param name="mode"/>
    <xsl:param name="source_dir" select="concat('file:////Users/terry/Github/m-k-manuscript-data/ms-xml/',$mode,'/')"/>
    <xsl:template match="/" name="it">
        <all>
        <xsl:variable name="folderURI" select="resolve-uri($source_dir)"/>
            <xsl:for-each select="collection(concat($folderURI, '?select=*.xml;recurse=yes'))">
                <xsl:apply-templates mode="copy" select="."/>
            </xsl:for-each>
        </all>
    </xsl:template>    
    <!-- Deep copy template -->
    <xsl:template match="node()|@*" mode="copy">
        <xsl:copy>
            <xsl:apply-templates mode="copy" select="@*"/>
            <xsl:apply-templates mode="copy"/>
        </xsl:copy>
    </xsl:template>
    <!-- Handle default matching -->
    <xsl:template match="*"/>
</xsl:stylesheet>
