#!/bin/bash

# Text to PDF Converter
# Converts one or more plain text files to PDF format with the same base filenames
# Supports optional column layout (default: 1 column)

# Default values
COLUMNS=1

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--columns)
            if [[ $2 =~ ^[1-9][0-9]*$ ]]; then
                COLUMNS="$2"
                shift 2
            else
                echo "Error: Invalid column count '$2'" >&2
                exit 1
            fi
            ;;
        --columns=*)
            if [[ "${1#*=}" =~ ^[1-9][0-9]*$ ]]; then
                COLUMNS="${1#*=}"
                shift
            else
                echo "Error: Invalid column count '${1#*=}'" >&2
                exit 1
            fi
            ;;
        -*)
            echo "Error: Unknown option '$1'" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Check if input files were provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide one or more text files as arguments" >&2
    echo "Usage: $0 [-c N|--columns=N] <file1> [file2] [file3] ..." >&2
    echo "  -c N, --columns=N  Set number of columns (default: 1)" >&2
    exit 1
fi

# Check for required dependencies
if ! command -v enscript &> /dev/null || ! command -v ps2pdf &> /dev/null; then
    echo "Error: Required packages 'enscript' and 'ghostscript' are not installed" >&2
    exit 1
fi

# Initialize counters
success_count=0
fail_count=0

# Process each file
for input_file in "$@"; do
    # Verify file exists
    if [ ! -f "$input_file" ]; then
        echo "Warning: File '$input_file' does not exist - skipping" >&2
        ((fail_count++))
        continue
    fi

    # Verify file is readable
    if [ ! -r "$input_file" ]; then
        echo "Warning: Cannot read file '$input_file' - skipping" >&2
        ((fail_count++))
        continue
    fi

    # Get filename without extension
    input_file="$(realpath "${input_file}")"
    base_name="${input_file%.*}"

    # Set output PDF filename
    output_file="${base_name}.pdf"

    # Perform conversion
    echo "Converting '$input_file' to '$output_file' (${COLUMNS} column(s))..."
    if [ "$COLUMNS" -eq 1 ]; then
        # Single column (direct conversion)
        enscript "$input_file" --output=- | ps2pdf - "$output_file"
    else
        # Multiple columns (using psnup if available)
        if command -v psnup &> /dev/null; then
            enscript "$input_file" --output=- | psnup -"$COLUMNS" | ps2pdf - "$output_file"
        else
            echo "Warning: 'psnup' not found - using enscript's native column support" >&2
            enscript "$input_file" --columns="$COLUMNS" --output=- | ps2pdf - "$output_file"
        fi
    fi

    # Check conversion status
    if [ $? -eq 0 ]; then
        echo "Success: Created '$output_file'"
        ((success_count++))
    else
        echo "Error: Failed to convert '$input_file'" >&2
        ((fail_count++))
    fi
done

# Print summary
echo "Conversion complete: $success_count succeeded, $fail_count failed"

# Exit with appropriate status
if [ $fail_count -gt 0 ]; then
    exit 1
else
    exit 0
fi
