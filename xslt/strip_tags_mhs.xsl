<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0" >
    <xsl:strip-space elements="*"/>
    <xsl:output encoding="UTF-8" method="text" />
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    <xsl:template match="id | margin | image | link"/>
<!--    <xsl:template match="head | ab | div | lb |page" mode="default">
        <xsl:apply-templates/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>

    -->
    <xsl:template match="head | ab |page">
        <xsl:apply-templates/>
    <xsl:text>&#10;</xsl:text>
    </xsl:template>
    
    <xsl:template match="div |corr | add">
        <xsl:text>&lt;</xsl:text>
        <xsl:value-of select="local-name()"/>
        <xsl:text>&gt;</xsl:text>
            <xsl:apply-templates/>
        <xsl:text>&lt;/</xsl:text>
        <xsl:value-of select="local-name()"/>
        <xsl:text>&gt;</xsl:text>
    </xsl:template>
    
    <xsl:template match="lb">
        <xsl:text>&lt;</xsl:text>
        <xsl:value-of select="'lb/'"/>
        <xsl:text>&gt;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:apply-templates/><xsl:text> </xsl:text>
    </xsl:template>
</xsl:stylesheet> 