#!/usr/bin/env python
"""
Insert soft hyphens into FB2 file.  Later this file can be converted into
Kindle format to enable hyphenation.  Russian and English hyphenation
is supported.
"""
import codecs
import sys
from xml.dom.minidom import parse
from hyphenator import hyphenate_word

SOFT_HYPHEN = u'\u00AD'

def parse_xml(input_file):
    dom = parse(input_file)
    for tag in ('p', 'v'):
        for node in dom.getElementsByTagName(tag):
            insert_hyphens(node)
    return dom

def insert_hyphens(node):
    if node.nodeType == node.TEXT_NODE:
        new_data = ' '.join([hyphenate_word(w, SOFT_HYPHEN) for w in node.data.split()])
        # Spaces are trimmed, we have to add them manually back
        if node.data.startswith(' '):
            new_data = ' ' + new_data
        if node.data.endswith(' '):
            new_data += ' '
        node.data = new_data
    for child in node.childNodes:
        insert_hyphens(child)

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'Usage: %s input_fb2_file output_fb2_file' % sys.argv[0]
        sys.exit(1)
    print 'Processing FB2 file...',
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    dom = parse_xml(input_file)
    with codecs.open(output_file, encoding='utf-8', mode='w') as f:
        dom.writexml(f, encoding='utf-8')
    print 'Done.'
