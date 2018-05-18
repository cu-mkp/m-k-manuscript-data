<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.0">
    <xsl:output method="text" encoding="UTF-8"/>
    
    <xsl:template match="/">
<!--        <xsl:text>folio</xsl:text>
        <xsl:text>:</xsl:text>
        <xsl:text>div_id</xsl:text>
        <xsl:text>:</xsl:text>
        <xsl:text>margin</xsl:text>
        <xsl:text>:</xsl:text>
        <xsl:text>heading</xsl:text>
        <xsl:text>:</xsl:text>
        <xsl:text>continued</xsl:text>
        <xsl:text>&#10;</xsl:text>
-->
        <xsl:apply-templates select="//div"/>

    </xsl:template>
    
    <xsl:template match="div">
        <xsl:value-of select="preceding::page"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="child::id"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="normalize-space(child::margin)"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="normalize-space(child::head)"/>
        <xsl:text>|</xsl:text>
        <xsl:if test="child::cont">
        <xsl:text>continued</xsl:text>
        </xsl:if>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
</xsl:stylesheet>