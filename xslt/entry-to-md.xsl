<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    exclude-result-prefixes="#all">

    <xsl:output encoding="UTF-8" method="text"/>
    <xsl:param name="mode"/>

    <xsl:param name="other-mode">
        <xsl:choose>
            <xsl:when test="$mode = 'tc'">
                <xsl:text>tl</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tl'">
                <xsl:text>tc</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tcn'">
                <xsl:text>tl</xsl:text>
            </xsl:when>
        </xsl:choose>
    </xsl:param>

    <xsl:param name="mode-expanded">
        <xsl:choose>
            <xsl:when test="$mode = 'tc'">
                <xsl:text>diplomatic</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tl'">
                <xsl:text>translation</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tcn'">
                <xsl:text>normalized</xsl:text>
            </xsl:when>
        </xsl:choose>
    </xsl:param>

    <xsl:param name="other-mode-expanded">
        <xsl:choose>
            <xsl:when test="$mode = 'tc'">
                <xsl:text>translation</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tl'">
                <xsl:text>diplomatic</xsl:text>
            </xsl:when>
            <xsl:when test="$mode = 'tcn'">
                <xsl:text>translation</xsl:text>
            </xsl:when>
        </xsl:choose>
    </xsl:param>

    <xsl:param name="folio_id" select="concat('p-', /root/page)"/>
    

    <xsl:template match="/">
        <xsl:apply-templates select="/root"/>
    </xsl:template>

    <!-- <xsl:strip-space elements="*"/>-->
    <xsl:param name="materials">
        <xsl:for-each select="distinct-values(//m[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="tools">
        <xsl:for-each select="distinct-values(//tl[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>


    <xsl:param name="animals">
        <xsl:for-each select="distinct-values(//al[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>


    <xsl:param name="plants">
        <xsl:for-each select="distinct-values(//pa[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="measurements">
        <xsl:for-each select="distinct-values(//ms[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="bodyparts">
        <xsl:for-each select="distinct-values(//bp[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="environments">
        <xsl:for-each select="distinct-values(//env[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:param name="places">
        <xsl:for-each select="distinct-values(//pl[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>


    <xsl:param name="professions">
        <xsl:for-each select="distinct-values(//pro[normalize-space()]/normalize-space())">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
    </xsl:param>

    <xsl:template match="root">
        <xsl:message select="$folio_id"></xsl:message>
        <xsl:message select="$materials"/>
        <xsl:result-document encoding="utf-8" href="../_texts/{$folio_id}_{$mode}.md">
            <!-- YAML for Ed -->
            <xsl:text>---&#x0A;layout: narrative&#x0A;</xsl:text>
            <xsl:text>title: </xsl:text>
            <xsl:value-of select="normalize-space(child::page)"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>identifier: </xsl:text>
            <xsl:value-of select="$folio_id"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>folio: </xsl:text>
            <xsl:value-of select="page"/>
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
            <xsl:text>mode: </xsl:text>
            <xsl:value-of select="$mode"/>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>editor: GR8975 Seminar Participants&#x0A;</xsl:text>
            <xsl:text>rights: Public Domain&#x0A;</xsl:text>
            <!--            <xsl:text>purposes: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($purposes, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>activities: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($activities, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
-->
            <!-- materials -->
            <xsl:text>materials: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($materials, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- tools-->
            <xsl:text>tools: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($tools, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- measurements -->
            <xsl:text>measurements: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($measurements, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- body parts -->
            <xsl:text>bodyparts: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($bodyparts, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- places -->
            <xsl:text>places: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($places, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- plants -->
            <xsl:text>plants: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($plants, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- professions -->
            <xsl:text>professions: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($professions, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- environments -->
            <xsl:text>environments: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($environments, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <!-- animals -->
            <xsl:text>animals: </xsl:text>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="translate(translate($animals, '[', ''), ']', '')"/>
            <xsl:text>]</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
            <xsl:text>---&#x0A;&#x0A;</xsl:text>

            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="head">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>## </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="head[parent::*[child::margin]]">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>** </xsl:text>
        <xsl:apply-templates/>
        <xsl:text> **</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="ab | div">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="*[child::margin]">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>*at&#160;</xsl:text>
        <xsl:value-of select="replace(margin[1]/text(), '-', ' ')"/>
        <xsl:text>&#160;margin</xsl:text>
        <xsl:text>*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select="replace(replace(replace(., '-', '—'), '\s+', ' '), '\+', '\\+')"/>
    </xsl:template>

    <!-- folio breaks and link to image -->
    <xsl:template match="page">
        <xsl:message select="$folio_id"></xsl:message>
        <!-- Navigation Links -->
        <xsl:text>&lt;p&gt;</xsl:text>
        <!-- TOC Link -->
        <xsl:text>&lt;a href="{{ site.baseurl }}/</xsl:text>
        <xsl:value-of select="$mode-expanded"/>
        <xsl:text>/"&gt;[TOC]&lt;/a&gt;</xsl:text>
        <!-- Link to Other Editions -->
        <xsl:text> | </xsl:text>
        <xsl:text>&lt;a href="{{ site.baseurl }}/_texts/</xsl:text>
        <xsl:value-of select="$folio_id"/>
        <xsl:text>_</xsl:text>
        <xsl:value-of select="$other-mode"/>
        <xsl:text>.md</xsl:text>
        <xsl:text>/"&gt;[</xsl:text>
        <xsl:value-of select="$other-mode-expanded"/>
        <xsl:text>]&lt;/a&gt;</xsl:text>
        <xsl:text>&lt;/p&gt;</xsl:text>
        <!-- page break -->
        <xsl:text>&lt;div class="folio" align="center"&gt;</xsl:text>
        <xsl:text>- - - - - &lt;a href="</xsl:text>
        <xsl:value-of select="following::image"/>
        <xsl:text>" target="_blank"&gt;</xsl:text>
        <xsl:text>&lt;img src="https://cu-mkp.github.io/2017-workshop-edition/assets/photo-icon.png" alt="folio image: " style="display:inline-block; margin-bottom:-3px;"/&gt;</xsl:text>
        <xsl:value-of select="normalize-space(.)"/>
        <xsl:text>&lt;/a&gt; - - - - -</xsl:text>
        <xsl:text> &lt;/div&gt;</xsl:text>
    </xsl:template>


    <!-- annotations -->
    <!--    <xsl:template match="annotations">
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
-->
    <xsl:template
        match="
            al |
            bp |
            cn |
            env |
            m |
            md |
            ms |
            mu |
            pa |
            pl |
            pn |
            pro |
            sn |
            tl |
            tmp |
            del |
            add |
            sup">
        <xsl:text>&lt;span class="</xsl:text>
        <xsl:value-of select="local-name()"/>
        <xsl:text>"&gt;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&lt;/span&gt;</xsl:text>
    </xsl:template>
    <!--    
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
-->
    <xsl:template match="figure[child::margin] | figure[child::link]">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>&gt; *Figure*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:if test="margin">
            <xsl:text>&gt; </xsl:text>
            <xsl:text>*at&#160;</xsl:text>
            <xsl:value-of select="replace(margin/text(), '-', ' ')"/>
            <xsl:text>&#160;margin</xsl:text>
            <xsl:text>*</xsl:text>
            <xsl:text>&#x0A;</xsl:text>
        </xsl:if>
        <xsl:text>&gt; </xsl:text>
        <xsl:text>&lt;a href="</xsl:text>
        <xsl:value-of select="link"/>
        <xsl:text>" target="_blank"&gt;</xsl:text>
        <xsl:text>&lt;img src="https://cu-mkp.github.io/GR8975-edition/assets/photo-icon.png" alt="Figure" style="display:inline-block; margin-bottom:-3px;"/&gt;</xsl:text>
        <xsl:text>&lt;/a&gt;</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

    <xsl:template match="id | margin | image"/>

    <xsl:template match="lb">
        <xsl:text>&lt;br/&gt;</xsl:text>
    </xsl:template>

    <xsl:template match="cont">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>*</xsl:text>
        <xsl:text>[continued]</xsl:text>
        <xsl:text>*</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
