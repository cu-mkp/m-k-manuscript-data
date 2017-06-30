<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:output encoding="UTF-8" method="xml"/>
    <xsl:include href="identity.xsl"/>
    
    <xsl:param name="al_vocab" select="document('/Users/terry/Github/ms-xml/vocab/al_vocab.xml')"></xsl:param>
    <xsl:key name="al_lookup" match="//row" use="verbatim"/>
    
    <xsl:template match="al">
        <xsl:variable name="term" select="normalize-space(./text())"/>
        <xsl:message><xsl:text>TERM: </xsl:text><xsl:value-of select="$term"/></xsl:message>
        <xsl:message><xsl:text>NORMAL: </xsl:text><xsl:value-of select="key('al_lookup', $term, $al_vocab)/prefLabel"/></xsl:message>
        <xsl:element name="al">
            <xsl:attribute name="normal">
                <xsl:value-of select="key('al_lookup', $term)//prefLabel"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>