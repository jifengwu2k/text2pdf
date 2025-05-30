# `chromecodepdf`

A Python script that converts code files into syntax-highlighted PDF documents using Chrome and Pygments.

## Features

- **Headless Chrome**: Renders HTML to PDF, ensuring consistent appearance across platforms.
- **Syntax Highlighting** using [Pygments](https://pygments.org/) for various programming languages.
- **Multiple Columns**: Use `--columns` to split the output into multiple columns.
- **Customizable Styles**: Specify a color style with `--style` (any supported Pygments style).
- **Python 2 & 3 compatible**
- **Windows & POSIX support**
- **Unicode-safe**, including non-ASCII paths

## Requirements

- **Chrome, Chromium, or Microsoft Edge**  
   - A headless Chrome executable must be installed and discoverable.  
   - If Chrome is not auto-detected, provide its path with `--chrome-path`.

## Usage

```
# Basic single-file conversion
python -m chromecodepdf file1.py

# Multiple files at once
python -m chromecodepdf script.sh code.c

# Specify columns
python -m chromecodepdf --columns=2 code.c

# Override default syntax style (e.g., 'friendly')
python -m chromecodepdf --style=friendly script.sh

# Specify a custom Chrome path (if auto-detection fails)
python -m chromecodepdf --chrome-path="/usr/bin/google-chrome" file1.py
```

## Example: Running on Windows with Non-ASCII Paths

Example command:

```
C:\Users\jifengwu2k\packages\chromecodepdf>python -m chromecodepdf -c 2 "..\..\路径 有空格\名字 有空 格.py"
```

> This example combines deep relative paths, Unicode, and spaces to demonstrate full Unicode and shell compatibility - a scenario where many tools break.
> ⚠️ **Note**: When used Windows, Unicode paths may appear garbled in the console (e.g., `璺緞...`).  
> This happens because the browser may output text encoded in **UTF-8**, while the Windows console expects **mbcs** (legacy ANSI code page). Simulate via `u'C:\\Users\\jifengwu\\路径 有空格\\名字 有空格.pdf'.encode('utf-8').decode('mbcs')`. 
> The file is still written correctly - this is a console display issue only.

Sample output:

```
INFO: Using Chrome executable C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
76882 bytes written to file C:\Users\jifengwu\璺緞 鏈夌┖鏍糪鍚嶅瓧 鏈夌┖鏍?pdfINFO: Success: Created 'C:\Users\jifengwu\路径 有空格\名字 有空格.pdf'
INFO: Conversion complete: 1 succeeded, 0 failed
```

## How It Works

1. Read the Source File: The script reads each file's content.
2. Apply Syntax Highlighting: Uses Pygments to convert code into HTML with inline styles.
3. Generate Temporary HTML: Wraps the highlighted code in an HTML template and saves it to a temporary HTML file.
4. Convert HTML to PDF: Launches headless Chrome (via the `--headless` flag) to produce a PDF, respecting multi-column CSS.
5. Cleanup: Deletes any temporary HTML files upon completion. Logs successes and failures.

## License

This script is released under the [MIT License](LICENSE).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.