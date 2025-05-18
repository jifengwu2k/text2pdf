# Text to PDF Converter

A simple Bash script that converts plain text files to PDF documents.

## Features

- Converts any plain text file (.txt, .log, etc.) to PDF
- Preserves the original filename (appends .pdf extension)
- Lightweight and command-line friendly
- Provides clear error messages for missing dependencies or files

## Requirements

- Linux/Unix environment
- `enscript` (for text to PostScript conversion)
- `ghostscript` (contains `ps2pdf` for PostScript to PDF conversion)

## Usage

```bash
# Convert single file
bash txt2pdf.sh notes.txt

# Convert multiple files
bash txt2pdf.sh file1.txt file2.txt file3.log

# Convert all text files in directory
bash txt2pdf.sh *.txt
```

This will create `input_file.pdf` in the same directory.

## How It Works

1. The script first validates the input file exists and is readable
2. Uses `enscript` to convert the text file to PostScript format
3. Pipes the output to `ps2pdf` to generate the final PDF
4. Outputs success/failure messages with the resulting filename

## License

This script is released under the [MIT License](LICENSE).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.
