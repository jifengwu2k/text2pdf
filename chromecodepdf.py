#!/usr/bin/env python
"""
Code to PDF Converter
Converts code files to PDF with syntax highlighting and multi-column layout using Chrome and Pygments
"""
from __future__ import print_function

import argparse
import logging
import os
import os.path
import re
import sys
import tempfile
from get_chrome_paths import get_chrome_paths
from posix_or_nt import posix_or_nt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from strcompat import filesystem_string_to_unicode, unicode_to_uri_string, utf_8_string_to_unicode

IS_NT = posix_or_nt() == 'nt'
if IS_NT:
    from proclaunch.nt import Process
else:
    from proclaunch.posix import Process


def path_to_file_uri(path):
    abspath = os.path.abspath(path)

    # Handle Windows peculiarities (drive letters, backslashes, etc.).
    forward_slash_as_sep = abspath.replace(os.sep, '/')

    if re.match(r'^[A-Za-z]:/', forward_slash_as_sep):
        # file:///C:/...
        return 'file:///' + forward_slash_as_sep[:3] + unicode_to_uri_string(
            filesystem_string_to_unicode(forward_slash_as_sep[3:]))
    elif abspath.startswith('//'):
        return 'file://' + unicode_to_uri_string(filesystem_string_to_unicode(forward_slash_as_sep[2:]))
    else:
        return 'file://' + unicode_to_uri_string(filesystem_string_to_unicode(forward_slash_as_sep))


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    parser = argparse.ArgumentParser(
        description='Convert text files to PDF with syntax highlighting',
    )

    parser.add_argument(
        'input_files',
        metavar='INPUT_FILE',
        nargs='+',
        help='Input text file(s)'
    )

    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='Input text file encoding'
    )

    parser.add_argument(
        '--columns',
        type=int,
        default=1,
        help='Number of columns'
    )

    parser.add_argument(
        '--style',
        default='default',
        help='Pygments color style (ref. https://pygments.org/styles/)'
    )

    parser.add_argument(
        '--chrome-path',
        default=None,
        help='Chrome executable path'
    )

    args = parser.parse_args()

    input_files = args.input_files

    encoding = args.encoding

    columns = args.columns

    style = args.style

    chrome_path = args.chrome_path

    if chrome_path is None:
        chrome_paths = get_chrome_paths()

        if not chrome_paths:
            print('Chrome executable not found.', file=sys.stderr)
            print('The system could not locate a valid Chrome installation automatically. To resolve this:',
                  file=sys.stderr)
            print('1. Ensure Chrome is installed on your system, or', file=sys.stderr)
            print('2. Manually specify the Chrome executable path using the --chrome-path argument', file=sys.stderr)
            print('Example usage:', file=sys.stderr)
            print('--chrome-path=/path/to/chrome/executable', file=sys.stderr)

            sys.exit(1)

        chrome_path = chrome_paths[0]

        logging.info('Using Chrome executable %s', chrome_path)

    success_count = 0
    fail_count = 0

    for input_file in input_files:
        input_file_absolute_path = os.path.abspath(input_file)
        input_file_name_with_ext = os.path.basename(input_file_absolute_path)
        input_file_absolute_path_without_ext = os.path.splitext(input_file_absolute_path)[0]
        output_file_absolute_path = input_file_absolute_path_without_ext + '.pdf'

        with open(input_file_absolute_path, 'rb') as fp:
            code = fp.read().decode(encoding)

        lexer = get_lexer_for_filename(input_file)

        formatter = HtmlFormatter(
            nowrap=True,
            noclasses=True,
            style=style,
        )

        highlighted = highlight(code, lexer, formatter)

        unicode_html_content = u'\n'.join([
            u'<!DOCTYPE html>',
            u'<html>',
            u'<head>',
            u'<meta charset="utf-8">',
            u'<title>%s</title>' % filesystem_string_to_unicode(input_file_name_with_ext),
            u'<style> .code-columns { column-count: %d; white-space: pre-wrap; word-break: break-word; font-family: monospace } </style>' % columns,
            u'</head>',
            u'<body>',
            u'<div class="code-columns">',
            highlighted,
            u'</div>',
            u'</body>',
            u'</html>',
        ])

        temp_html_fd, temp_html_path = tempfile.mkstemp(suffix='.html')

        os.write(temp_html_fd, unicode_html_content.encode('utf-8'))

        arguments = [
            filesystem_string_to_unicode(chrome_path),
            u'--headless',
            u'--disable-gpu',
            u'--print-to-pdf=' + filesystem_string_to_unicode(output_file_absolute_path),
            u'--no-sandbox',
            utf_8_string_to_unicode(path_to_file_uri(temp_html_path))
        ]

        process = Process.from_arguments(arguments)
        process.run()
        process.wait()

        if os.path.isfile(output_file_absolute_path):
            logging.info("Success: Created '%s'", output_file_absolute_path)
            success_count += 1
        else:
            logging.error("Error: Failed to convert '%s'", input_file_absolute_path)
            fail_count += 1

        os.close(temp_html_fd)
        os.unlink(temp_html_path)

    logging.info("Conversion complete: %d succeeded, %d failed", success_count, fail_count)

    sys.exit(1 if fail_count > 0 else 0)
