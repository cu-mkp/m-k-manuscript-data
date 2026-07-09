#!/usr/bin/env python3
"""
Making and Knowing Project — DCE branding for generated PDFs.

Provides the header (M&K banner logo, linked to the online edition) and the
footer used across https://edition640.makingandknowing.org/, for placement on
the first page of each generated PDF. See issue #2130.

Assets are bundled in lib/assets/ so builds do not depend on the network.
Text that this module generates is localised; link targets are the edition's
own pages and are unchanged.
"""

from pathlib import Path

EDITION_URL = 'https://edition640.makingandknowing.org/'
LICENSE_URL = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
DOI_URL = 'https://doi.org/10.7916/78yt-2v41'

FOOTER_LABELS = {
    'en': {
        'project': 'Making and Knowing Project.',
        'licensed_under': 'Licensed under',
        'license_name': 'CC BY-NC-SA 4.0',
        'privacy': 'Privacy Notice',
        'disability': 'Disability Services',
        'nondiscrimination': 'Non-Discrimination',
        'banner_alt': 'Making and Knowing Project — Secrets of Craft and Nature',
        'license_alt': 'Creative Commons BY-NC-SA 4.0 licence',
        'columbia_alt': 'Columbia University',
        'center_alt': 'Center for Science and Society, Columbia University',
    },
    'fr': {
        'project': 'Making and Knowing Project.',
        'licensed_under': 'Sous licence',
        'license_name': 'CC BY-NC-SA 4.0',
        'privacy': 'Avis de confidentialité',
        'disability': 'Services aux personnes handicapées',
        'nondiscrimination': 'Non-discrimination',
        'banner_alt': 'Making and Knowing Project — Secrets of Craft and Nature',
        'license_alt': 'Licence Creative Commons BY-NC-SA 4.0',
        'columbia_alt': 'Université Columbia',
        'center_alt': 'Center for Science and Society, Université Columbia',
    },
}


def header_html(assets='../lib/assets', lang='en'):
    """M&K banner logo, top-left of the page, linking to the online edition."""
    t = FOOTER_LABELS[lang]
    return (f'<div class="mk-header">'
            f'<a href="{EDITION_URL}">'
            f'<img src="{assets}/mk-banner-logo.png" alt="{t["banner_alt"]}"/>'
            f'</a></div>\n')


def _cc_icons():
    """The four Creative Commons glyphs used in the edition's footer (white)."""
    path = Path(__file__).with_name('assets') / 'cc_icons.svg.txt'
    return ' '.join(path.read_text().split('\n'))


def footer_html(assets='../lib/assets', lang='en'):
    """The footer used on every page of the online edition."""
    t = FOOTER_LABELS[lang]
    return f'''<div class="mk-footer">
    <p class="mk-footer-license">
        <a class="mk-cc" href="{LICENSE_URL}" title="{t['license_alt']}">{_cc_icons()}</a>
        <span>{t['project']} {t['licensed_under']} <a href="{LICENSE_URL}">{t['license_name']}</a></span>
    </p>
    <p class="mk-footer-logos">
        <img class="mk-logo-columbia" src="{assets}/logo_columbia.png" alt="{t['columbia_alt']}"/>
        <img class="mk-logo-center" src="{assets}/logo_center_multi_line.png" alt="{t['center_alt']}"/>
    </p>
    <p class="mk-footer-links">
        <a href="https://cuit.columbia.edu/privacy-notice">{t['privacy']}</a>
        <span> | </span>
        <a href="http://health.columbia.edu/disability-services">{t['disability']}</a>
        <span> | </span>
        <a href="http://eoaa.columbia.edu/columbia-university-non-discrimination-statement-and-policy">{t['nondiscrimination']}</a>
    </p>
    <p class="mk-footer-doi">DOI: <a href="{DOI_URL}">{DOI_URL}</a></p>
</div>
'''


CSS = '''
    /* --- DCE branding (issue #2130): first page only --- */
    .mk-header {
        text-align: left;
        margin-bottom: 0.4in;
    }
    .mk-header img {
        width: 2.6in;
    }
    /* the edition's footer is a dark maroon bar with white type; the
       institution logos are white-on-transparent and need it */
    .mk-footer {
        text-align: center;
        font-size: 8pt;
        color: #fafafa;
        background-color: #460c0a;
        padding: 10pt 12pt;
        margin-top: 0.4in;
    }
    .mk-footer a {
        color: #fafafa;
        text-decoration: none;
    }
    .mk-footer p {
        margin: 4pt 0;
    }
    .mk-footer .mk-cc svg {
        vertical-align: middle;
        margin-right: 1pt;
    }
    .mk-footer-logos img {
        vertical-align: middle;
        margin: 0 6pt;
    }
    .mk-footer-logos .mk-logo-columbia { width: 1.6in; }
    .mk-footer-logos .mk-logo-center { width: 1.4in; }
    .mk-footer-doi { font-size: 7.5pt; }
    .mk-footer-links { font-size: 7.5pt; }
'''
