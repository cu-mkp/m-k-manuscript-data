<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output encoding="UTF-8" method="text"/>
    <xsl:param name="fieldSep"><xsl:text>	</xsl:text></xsl:param>
    <xsl:template match="/">
        <xsl:text>folio</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>entry_id</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>entry_title</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>fig_text</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>id</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>link</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>caption</xsl:text>
        <xsl:value-of select="$fieldSep"/>
        <xsl:text>TYPE</xsl:text>
        <xsl:text>&#10;</xsl:text>
        <xsl:apply-templates select="//figure"/>
    </xsl:template>

    <xsl:template match="figure">
        <xsl:value-of select="preceding::page[1]"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:value-of select="ancestor::div[1]/id"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:value-of select="ancestor::div[1]/head[1]/normalize-space()"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:value-of select="child::text()/normalize-space()"/>
        <xsl:value-of select="m/normalize-space()"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:apply-templates select="id"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:apply-templates  select="link"/>
        <xsl:value-of select="$fieldSep"/>
        <xsl:for-each select="caption">
            <xsl:value-of select="normalize-space()"/>
            <xsl:if test="position != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>	</xsl:text>
        <xsl:choose>
            <xsl:when test="not(child::id)"><xsl:text>MARK</xsl:text></xsl:when>
            <xsl:otherwise><xsl:text>GRAPHIC</xsl:text></xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>
    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>
</xsl:stylesheet>
