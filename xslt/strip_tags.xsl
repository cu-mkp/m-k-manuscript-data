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
    
    <!-- do not process -->
    <xsl:template match="id | margin | image | link | comment | render"/>

    <!-- line breaks before and after element -->
    <xsl:template match="ab | div">
        <xsl:text>&#10;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    
    <!-- line breaks after element -->
    <xsl:template match="lb | head">
        <xsl:apply-templates/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    
    <!-- place folio number on own line surrounded by strings of tildes -->
    <xsl:template match="root">
        <xsl:text>&#10;</xsl:text>
        <xsl:text>~~~~~~~~~~~~~~~</xsl:text>
        <xsl:value-of select="@page"/>
        <xsl:text>~~~~~~~~~~~~~~~</xsl:text>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    
    <!-- wrap exp in curly braces -->
    <xsl:template match="exp">
        <xsl:text>{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>
    
    <!-- do not process figures with child elements -->
    <xsl:template match="figure[child::*]">
        <xsl:message>figure with child</xsl:message>
    </xsl:template>
    
    <!-- process figure elements not containing child elements (i.e., only text) -->
    <xsl:template match="figure[not(child::*)]">
        <xsl:message>figure without child</xsl:message>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- by default, process all elements -->
    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- normalize spacing of text nodes 
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>
    -->
    
</xsl:stylesheet> 