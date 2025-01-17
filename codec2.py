import os
import argparse
import logging
import sys
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor  # noqa: F401

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_files(directory: str, valid_extensions: tuple, skip_extensions: tuple, skip_folders: list) -> list:
    """Find all valid files in the specified directory, skipping specified folders."""
    file_list = []
    
    for root, dirs, files in os.walk(directory):
        # Remove directories that are in the skip_folders list
        dirs[:] = [d for d in dirs if d not in skip_folders]

        for file in files:
            if (file.endswith(valid_extensions) and 
                not file.endswith(skip_extensions)):
                file_list.append(os.path.join(root, file))
    
    return file_list

def process_file(file_info: tuple) -> tuple:
    """Read the content of a file and return its path and content."""
    file_path, base_directory, include_full_path = file_info
    try:
        relative_path = file_path if include_full_path else os.path.relpath(file_path, base_directory)

        with open(file_path, 'r', encoding='utf-8') as content_file:
            content = content_file.read()

        return (relative_path, content)
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return (relative_path, None)

def create_summary_file(file_list: list, output_file: str) -> None:
    """Create a summary file with the contents of each file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for relative_path, content in tqdm(file_list, desc="Writing files", unit="file"):
            f.write(f"Path: {relative_path}\n")
            f.write("=" * len(relative_path) + "\n")
            if content is not None:
                f.write(content + "\n")
            f.write("-------------------------------------------------\n\n")

def validate_arguments(args) -> None:
    """Validate command-line arguments."""
    if not os.path.isdir(args.directory):
        raise ValueError(f"The provided directory '{args.directory}' does not exist.")
    
    if args.extensions and not all(ext.startswith('.') for ext in args.extensions):
        raise ValueError("All valid extensions must start with a dot (e.g., .txt).")

    if args.skip and not all(ext.startswith('.') for ext in args.skip):
        raise ValueError("All skip extensions must start with a dot (e.g., .jpg).")

def main() -> None:
    """Main execution function."""
    # Set up argument parser
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

        # Convert skip extensions and valid extensions from list of strings to tuples
        skip_extensions = tuple(args.skip) if args.skip else ()
        
        valid_extensions = tuple(args.extensions) if args.extensions else (
            '.txt', '.py', '.c', '.cpp', '.h', 
            '.cs', '.cake', '.cshtml', '.csx', 
            '.ps1', '.vbs', 
            '.js', '.mjs', 
            '.ts', 
            '.svelte',  # Commonly used for Svelte components
            '.rb', 
            '.rs', 
            '.html', '.htm', '.xhtml',
            '.css', 
            '.dart',
            '.jsx',  # Commonly used for ReactJS components
            '.bat',
            '.autoexe',
            # Additional extensions
            '.sh',  # Shell scripts
            '.bash',
            '.php', '.phtml',
            '.pl', '.pm',
            '.sql',
            '.xml',
            '.csv'
        )


        skip_folders = args.skip_folders if args.skip_folders else []

        found_files = find_files(args.directory, valid_extensions, skip_extensions, skip_folders)

        if found_files:
            file_info_list = [(file, args.directory, args.full_path) for file in found_files]

            with Pool(processes=cpu_count()) as pool:
                results = pool.map(process_file, file_info_list)

            logging.info("Processing completed. Writing summary...")
            create_summary_file(results, args.output)
            logging.info(f'Summary created: {args.output}')
        else:
            logging.warning('No matching files found.')

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
