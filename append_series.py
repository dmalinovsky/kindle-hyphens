#!/usr/bin/env python
"""
Appends FB2 series number and title to Kindle book title.
"""
import os
import subprocess
import sys
import tempfile
from xml.dom.minidom import parse

META_SERIES = 'calibre:series'
META_SERIES_INDEX = 'calibre:series_index'
META_TITLE = 'dc:title'
MOBI_FILE_TEMPLATE = '%s.azw3'
TITLE_TEMPLATE = '[%(index)02d] %(title)s (%(series)s)'


def extract_meta(fb2_file):
    (_, meta_file) = tempfile.mkstemp()

    try:
        subprocess.check_call(['ebook-meta', fb2_file,
            '--to-opf=%s' % meta_file])
        dom = parse(meta_file)
    finally:
        os.unlink(meta_file)
    meta = {n.getAttribute('name'):n.getAttribute('content')
            for n in dom.getElementsByTagName('meta')}
    meta[META_TITLE] = dom.getElementsByTagName(
            META_TITLE)[0].childNodes[0].data

    return meta


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print """Usage: %s fb2_file
Title is written into <fb2_file>.azw3 file.
To extract FB2 meta-data ebook-meta calibre script is used.""" % sys.argv[0]
        sys.exit(1)

    input_file = sys.argv[1]
    meta = extract_meta(input_file)
    if not META_SERIES in meta or not META_SERIES_INDEX in meta or \
        int(meta[META_SERIES_INDEX] <= 0):
        print 'Found no series meta data in %s' % input_file
        sys.exit(0)

    subprocess.check_call(['ebook-meta', MOBI_FILE_TEMPLATE % input_file,
        '-t', TITLE_TEMPLATE % {
            'series': meta[META_SERIES],
            'title': meta[META_TITLE],
            'index': int(meta[META_SERIES_INDEX]),
        }])
