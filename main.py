#!/usr/bin/env python
"""
Insert soft hyphens into FB2 file.  Later this file can be converted into
Kindle format to enable hyphenation.  Russian and English hyphenation
is supported.
"""
import codecs
from lxml import etree
import sys

from hyphenator import Hyphenator

SOFT_HYPHEN = u'\u00AD'

def parse_xml(input_file):
    dom = etree.parse(input_file, parser=etree.XMLParser(recover=True))
    # Fallback language is Russian ;)
    lang = detect_language(dom) or 'ru'
    hyphenator = Hyphenator(lang)
    for tag in ('p', 'v', 'text-author'):
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

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'Usage: %s input_fb2_file output_fb2_file' % sys.argv[0]
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print 'Processing %s...' % input_file,
    sys.stdout.flush()
    dom = parse_xml(input_file)
    with codecs.open(output_file, mode='w') as f:
        f.write(etree.tostring(dom.getroot(), encoding='UTF-8',
            xml_declaration=True))
    print 'Done.'
