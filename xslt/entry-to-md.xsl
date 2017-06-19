<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    exclude-result-prefixes="#all">

    <xsl:output encoding="UTF-8" method="text"/>

    <xsl:template match="/">
        <xsl:apply-templates select="/entry"/>
    </xsl:template>

    <!-- <xsl:strip-space elements="*"/>-->
    <xsl:param name="materials">
        <xsl:for-each select="distinct-values(//material[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="tools">
        <xsl:for-each select="distinct-values(//tool[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>
    
    
    <xsl:param name="animals">
        <xsl:for-each select="distinct-values(//animal[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>
    
    
    <xsl:param name="plants">
        <xsl:for-each select="distinct-values(//plant[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>
    
    
    <xsl:param name="colors">
        <xsl:for-each select="distinct-values(//color[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="activities">
        <xsl:for-each select="distinct-values(//activity[@type]/@type)">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>
    
    <xsl:param name="purposes">
        <xsl:for-each select="distinct-values(//purpose[@type]/@type)">
            <xsl:value-of select="."/><xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>


    <xsl:template match="entry">
        <xsl:message select="$materials"/>
        <xsl:variable name="sect_id" select="@identifier"/>
        <xsl:result-document encoding="utf-8" href="../_texts/{$sect_id}.md">
            <!-- YAML for Ed -->
            <xsl:text>---&#x0A;layout: narrative&#x0A;</xsl:text>
            <xsl:text>title: </xsl:text>
            <xsl:value-of select="normalize-space(child::heading)"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>identifier: </xsl:text>
            <xsl:value-of select="@identifier"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>folio: </xsl:text>
            <xsl:value-of select="child::folio[1]/@number"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>annotation: </xsl:text>
            <xsl:choose>
                <xsl:when test="//annotations/annotation[@title][1]">
                    <xsl:text>yes</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>no</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
             <xsl:text>&#x0A;</xsl:text>
            <xsl:text>author:</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>mode: annotated</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>editor: GR8975 Seminar Participants&#x0A;</xsl:text>
            <xsl:text>rights: Public Domain&#x0A;</xsl:text>
            <xsl:text>purposes: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($purposes, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>activities: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($activities, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>materials: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($materials, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>tools: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($tools, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>colors: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($colors, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>plants: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($plants, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>animals: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($animals, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>---&#x0A;&#x0A;</xsl:text>

            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="heading">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>## </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="block">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="margin-block | block[@position]">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>*at&#160;</xsl:text>
        <xsl:value-of select="replace(@position, '-', ' ')"/>
        <xsl:text>&#160;margin of folio </xsl:text>
        <xsl:value-of select="preceding::folio[1]/@number"/>
        <xsl:text>*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text><xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select="replace(replace(replace(., '-', '—'), '\s+', ' '), '\+', '\\+')"/>
    </xsl:template>

    <!-- folio breaks and link to image -->
    <xsl:template match="folio">
        <xsl:text>&lt;div class="folio" align="center"&gt;</xsl:text>
        <xsl:text>- - - - - &lt;a href="</xsl:text>
        <xsl:value-of select="@url"/>
        <xsl:text>" target="_blank"&gt;</xsl:text>
        <xsl:text>&lt;img src="https://cu-mkp.github.io/GR8975-edition/assets/photo-icon.png" alt="folio image: " style="display:inline-block; margin-bottom:-3px;"/&gt;</xsl:text>
        <xsl:value-of select="@number"/>
        <xsl:text>&lt;/a&gt; - - - - -</xsl:text>
        <xsl:text> &lt;/div&gt;</xsl:text>
    </xsl:template>
    
    
    <!-- annotations -->
    <xsl:template match="annotations">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&lt;div class="annotation" align="left"&gt;</xsl:text>
        <xsl:text>Annotations:</xsl:text>
        <xsl:apply-templates select="annotation"/>
        <xsl:text> &lt;/div&gt;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

<xsl:template match="annotation">
    <xsl:text>&#x0A;</xsl:text>
    <xsl:text>&lt;a href="</xsl:text>
    <xsl:value-of select="@url"/>
    <xsl:text>" target="_blank"&gt;</xsl:text>
    <xsl:value-of select="@title"/>
    <xsl:text>&lt;/a&gt;</xsl:text>
    <xsl:text>&#x0A;</xsl:text>
   </xsl:template>

    <xsl:template match="purpose">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template
        match="
            activity | animal | foreign
            | material | material_format | place | plant
            | profession | image | ref | sub_recipe | tool | unit | color | name | q
            | sup | time">
        <xsl:text>&lt;span class="</xsl:text>
        <xsl:value-of select="local-name()"/>
        <xsl:text>"&gt;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&lt;/span&gt;</xsl:text>
    </xsl:template>
    
    <xsl:template match="list">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>
    
    <xsl:template match="item">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>- {:.indent-3}</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>
    
    <xsl:template match="figure">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; *Figure*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:if test="@position">
        <xsl:text>&gt; </xsl:text>       
        <xsl:text>*at&#160;</xsl:text>
        <xsl:value-of select="replace(@position, '-', ' ')"/>
        <xsl:text>&#160;margin of folio </xsl:text>
        <xsl:value-of select="preceding::folio[1]/@number"/>
        <xsl:text>*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        </xsl:if>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>&lt;a href="</xsl:text>
        <xsl:value-of select="@url"/>
        <xsl:text>" target="_blank"&gt;</xsl:text>
        <xsl:text>&lt;img src="https://cu-mkp.github.io/GR8975-edition/assets/photo-icon.png" alt="Figure" style="display:inline-block; margin-bottom:-3px;"/&gt;</xsl:text>
        <xsl:text>&lt;/a&gt;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>
</xsl:stylesheet>
