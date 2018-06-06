<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.1">
    
    <xsl:output encoding="UTF-8" method="xml"/>

    <xsl:template match="node()">
        <xsl:copy>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="page | image | id | margin | cont | link"></xsl:template>

    <xsl:template match="root | div | ab | figure">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="page | image | id | margin | cont | link" mode="make_attr"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    
    <xsl:template match="page | image | id | margin |link" mode="make_attr">
        <xsl:attribute name="{local-name()}"><xsl:value-of select="normalize-space(.)"/></xsl:attribute>
    </xsl:template>
    
    <xsl:template match="cont[not(following-sibling::*)]" mode="make_attr">
        <xsl:attribute name="continued"><xsl:text>yes</xsl:text></xsl:attribute>
    </xsl:template>
    
    <xsl:template match="cont[not(preceding-sibling::*)]" mode="make_attr">
        <xsl:attribute name="continues"><xsl:text>yes</xsl:text></xsl:attribute>
    </xsl:template>
    
</xsl:stylesheet>