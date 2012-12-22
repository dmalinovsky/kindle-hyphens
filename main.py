#!/usr/bin/env python
"""
Insert soft hyphens into FB2 file.  Later this file can be converted into
Kindle format to enable hyphenation.  Russian and English hyphenation
is supported.
"""
import codecs
import sys
from xml.dom.minidom import parse
from hyphenator import Hyphenator

SOFT_HYPHEN = u'\u00AD'

def parse_xml(input_file):
    dom = parse(input_file)
    # Fallback language is Russian ;)
    lang = detect_language(dom) or 'ru'
    hyphenator = Hyphenator(lang)
    for tag in ('p', 'v', 'text-author'):
        for node in dom.getElementsByTagName(tag):
            insert_hyphens(node, hyphenator)
    return dom

def detect_language(dom):
    node = dom.getElementsByTagName('lang')
    if not node:
        return False
    node = node[0].childNodes
    if not node:
        return False
    node = node[0]
    if node.nodeType == node.TEXT_NODE:
        return node.data
    else:
        return False

def insert_hyphens(node, hyphenator):
    if node.nodeType == node.TEXT_NODE:
        new_data = ' '.join([hyphenator.hyphenate_word(w, SOFT_HYPHEN)
            for w in node.data.split()])
        # Spaces are trimmed, we have to add them manually back
        if node.data.startswith(' '):
            new_data = ' ' + new_data
        if node.data.endswith(' '):
            new_data += ' '
        node.data = new_data
    for child in node.childNodes:
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
    with codecs.open(output_file, encoding='utf-8', mode='w') as f:
        dom.writexml(f, encoding='utf-8')
    print 'Done.'
