#!/usr/bin/env python
"""
Insert soft hyphens into FB2 file.  Later this file can be converted into
Kindle format to enable hyphenation.  Russian and English hyphenation
is supported.
"""
import codecs
from lxml import etree
import os
import sys

from hyphenator import Hyphenator

SOFT_HYPHEN = u'\u00AD'

def parse_xml(input_file):
    dom = etree.parse(input_file, parser=etree.XMLParser(recover=True))
    # Fallback language is Russian ;)
    lang = detect_language(dom) or 'ru'
    return process_dom(dom, lang)

def process_dom(dom, lang):
    hyphenator = Hyphenator(lang)
    for tag in ('p', 'v', 'text-author', 'div'):
        for node in dom.xpath("//*[local-name() = '%s']" % tag):
            insert_hyphens(node, hyphenator)
    return dom

def detect_language(dom):
    nodes = dom.xpath("//*[local-name() = 'lang']")
    return nodes[0].text if nodes else False

def insert_hyphens(node, hyphenator):
    for attr in ('text', 'tail'):
        text = getattr(node, attr)
        if not text:
            continue
        new_data = ' '.join([hyphenator.hyphenate_word(w, SOFT_HYPHEN)
            for w in text.split()])
        # Spaces are trimmed, we have to add them manually back
        if text.startswith(' '):
            new_data = ' ' + new_data
        if text.endswith(' '):
            new_data += ' '
        setattr(node, attr, new_data)

    for child in node.iterchildren():
        insert_hyphens(child, hyphenator)

def process_epub_file(container):
    if container.is_drm_encrypted():
        print 'ERROR - cannot remove unused images from DRM encrypted book'
        return False

    dirtied = False
    for name in container.get_html_names():
        html = container.get_raw(name)
        dom = etree.XML(html, parser=etree.XMLParser(recover=True))

        # Detect language
        # OPS/content.opf <dc:language>
        language = container.opf.xpath("//*[local-name() = 'language']")[0]
        dom = process_dom(dom, language.text)
        new_html = etree.tostring(dom, encoding='UTF-8', xml_declaration=True)
        dirtied = True
        container.set(name, new_html)
    return dirtied

def process_epub(input_file, output_file):
    from calibre import CurrentDir
    from calibre.libunzip import extract as zipextract
    from calibre.ptempfile import TemporaryDirectory
    from calibre.utils.logging import Log

    from calibre_plugins.modify_epub.container import ExtendedContainer

    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)

    # Extract the epub into a temp directory
    with TemporaryDirectory('fb2-hyphens') as tdir:
        with CurrentDir(tdir):
            zipextract(input_file, tdir)

            # Use our own simplified wrapper around an ePub that will
            # preserve the file structure and css
            container = ExtendedContainer(tdir, Log())
            is_modified = process_epub_file(container)
            if is_modified:
                container.write(output_file)

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print """Usage: %s input_file output_file
        FB2 and ePub formats are supported.""" % sys.argv[0]
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    (_, ext) = os.path.splitext(input_file.lower())
    if ext not in ('.epub', '.fb2'):
        print 'Only ePub and FB2 formats are supported'
        sys.exit(1)
    print 'Processing %s...' % input_file,
    sys.stdout.flush()
    if ext == '.fb2':
        dom = parse_xml(input_file)
        with codecs.open(output_file, mode='w') as f:
            f.write(etree.tostring(dom.getroot(), encoding='UTF-8',
                xml_declaration=True))
    else:
        process_epub(input_file, output_file)
    print 'Done.'
