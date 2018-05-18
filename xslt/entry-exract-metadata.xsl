<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
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
        <xsl:value-of select="child::id"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="normalize-space(child::head)"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="ancestor::root/page"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="normalize-space(child::margin)"/>
        <xsl:text>|</xsl:text>
        <xsl:if test=".//figure">
            <xsl:text>CONTAINS FIGURE</xsl:text>
        </xsl:if>
        <xsl:text>|</xsl:text>
        <xsl:if test="child::cont">
            <xsl:text>continued</xsl:text>
        </xsl:if>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//al/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//bp/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//cn/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//env/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//m/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//ms/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//pa/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//pl/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//pn/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//pro/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//sn/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//tl/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//md/normalize-space())">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
            <xsl:text>;</xsl:text>
        </xsl:if>
        </xsl:for-each>
        <xsl:text>|</xsl:text>
        <xsl:for-each select="distinct-values(.//mu/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">
                <xsl:text>;</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
