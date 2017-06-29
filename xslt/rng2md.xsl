<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:rng="http://relaxng.org/ns/structure/1.0"
    xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    
    
    <xsl:template match="rng:define">
        <xsl:text>&#10;</xsl:text>
        <xsl:text>## </xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>&#10;</xsl:text>
        
    </xsl:template>
    
</xsl:stylesheet>