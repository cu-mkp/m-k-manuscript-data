<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output encoding="UTF-8" method="xhtml"/>
    <xsl:template match="/">
        <html>
            <head><title>Material Terms (TL)</title></head>
            <body>
                <h2>Material Terms (TL)</h2>
                <xsl:for-each-group select="//row" group-by="prefLabel">
                    <xsl:sort select="prefLabel"/>
                    <h3>
                        <xsl:value-of select="current-grouping-key()"/><xsl:text> (</xsl:text>
                        <xsl:value-of select="count(current-group())"/><xsl:text>)</xsl:text>
                    </h3>
                    <ul>
                        <xsl:for-each select="current-group()//verbatimTerm">
                            <li>
                                <xsl:value-of select="."/>
                                <xsl:text>: </xsl:text> <i><xsl:value-of select="following-sibling::entry"/></i><xsl:text> (</xsl:text><xsl:value-of select="following-sibling::folio"/>
                                <xsl:text>)</xsl:text>
                            </li>
                        </xsl:for-each>
                    </ul>
                </xsl:for-each-group>

            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
