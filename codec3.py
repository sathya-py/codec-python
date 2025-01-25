import argparse
import logging
import sys
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import gzip
import chardet  # Make sure to install this library

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_files(directory: Path, valid_extensions: tuple, skip_extensions: tuple, skip_folders: list) -> list:
    """Find all valid files in the specified directory, skipping specified folders."""
    file_list = []
    
    for path in directory.rglob('*'):
        if path.is_file():
            if (path.suffix in valid_extensions and 
                path.suffix not in skip_extensions and 
                path.parent.name not in skip_folders):
                file_list.append(path)
    
    return file_list

def detect_encoding(file_path: Path) -> str:
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Read first 10k bytes for encoding detection
        result = chardet.detect(raw_data)
        return result['encoding']

def process_file(file_path: Path, base_directory: Path, include_full_path: bool) -> tuple:
    """Read the content of a file and return its path and content."""
    try:
        relative_path = str(file_path) if include_full_path else str(file_path.relative_to(base_directory))

        # Check if the file is a gzip file
        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rb') as f:
                content = f.read()
                return (relative_path, content.decode('utf-8', errors='replace'))  # Decode with error handling

        # For regular text files, detect encoding first
        encoding = detect_encoding(file_path)
        with file_path.open('r', encoding=encoding, errors='replace') as content_file:
            content = content_file.read()

        return (relative_path, content)
    
    except UnicodeDecodeError as e:
        logging.error(f"Unicode decode error for file {file_path}: {e}")
        return (relative_path, "Error reading content")
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return (relative_path, "Error processing file")

def create_summary_file(file_list: list, output_file: str) -> None:
    """Create a summary file with the contents of each file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for relative_path, content in tqdm(file_list, desc="Writing files", unit="file"):
            f.write(f"Path: {relative_path}\n")
            f.write("=" * len(relative_path) + "\n")
            if "Error" not in content:
                f.write(content + "\n")
            else:
                f.write(content + "\n")  # Write error message instead of content
            f.write("-------------------------------------------------\n\n")

def validate_arguments(args) -> None:
    """Validate command-line arguments."""
    if not Path(args.directory).is_dir():
        raise ValueError(f"The provided directory '{args.directory}' does not exist.")
    
    if args.extensions and not all(ext.startswith('.') for ext in args.extensions):
        raise ValueError("All valid extensions must start with a dot (e.g., .txt).")

    if args.skip and not all(ext.startswith('.') for ext in args.skip):
        raise ValueError("All skip extensions must start with a dot (e.g., .jpg).")

def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Find specified files in a directory.')
    parser.add_argument('directory', type=str, help='The directory to search in')
    parser.add_argument('-o', '--output', type=str, default='summary.txt',
                        help='Output summary file name (default: summary.txt)')
    parser.add_argument('-s', '--skip', type=str, nargs='*', 
                        help='List of extensions to skip (e.g., .ico .jpg)')
    parser.add_argument('-e', '--extensions', type=str, nargs='*', 
                        help='List of valid extensions to look for (e.g., .txt .dart .json)')
    parser.add_argument('--full-path', action='store_true',
                        help='Include full paths in the output')
    parser.add_argument('--skip-folders', type=str, nargs='*',
                        help='List of folder names to skip (e.g., folder1 folder2)')

    # Check for no arguments and show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    try:
        validate_arguments(args)

        skip_extensions = tuple(args.skip) if args.skip else ()
        valid_extensions = tuple(args.extensions) if args.extensions else (
            '.txt', '.py', '.c', '.cpp', '.h', 
            '.cs', '.cake', '.cshtml', '.csx', 
            '.ps1', '.vbs', 
            '.js', '.mjs', 
            '.ts', 
            '.svelte',
            '.rb',
            '.rs',
            '.html', '.htm', '.xhtml',
            '.css',
            '.dart',
            '.jsx',
            '.bat',
            '.autoexe',
            # Additional extensions
            '.sh',
            '.bash',
            '.php', '.phtml',
            '.pl', '.pm',
            '.sql',
            '.xml',
            '.csv'
        )

        skip_folders = args.skip_folders if args.skip_folders else []

        found_files = find_files(Path(args.directory), valid_extensions, skip_extensions, skip_folders)

        logging.info(f"Found {len(found_files)} matching files.")

        if found_files:
            with Pool(processes=cpu_count()) as pool:
                results = pool.starmap(process_file, [(file, Path(args.directory), args.full_path) for file in found_files])

            logging.info("Processing completed. Writing summary...")
            create_summary_file(results, args.output)
            logging.info(f'Summary created: {args.output}')
        else:
            logging.warning('No matching files found.')

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
