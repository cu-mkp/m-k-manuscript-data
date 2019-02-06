<?xml version="1.0" encoding="UTF-8"?>
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
        <xsl:import href="strip_tags.xsl"/>
        <xsl:output encoding="UTF-8" method="xml"/>
        <xsl:template match="/">
            <xsl:apply-templates select="//div[child::id]"/>
        </xsl:template>
        <xsl:template match="div">
            <xsl:variable name="div-id" select="concat('p', preceding::page[1], '_', position())"/>
            <xsl:message select="$div-id"/>
            <xsl:result-document encoding="utf-8" method="text" href="../entries/tl/{$div-id}_tl.txt">
               <xsl:apply-imports/>
            </xsl:result-document>
        </xsl:template>
</xsl:stylesheet>