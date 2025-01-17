import os
import argparse
from tqdm import tqdm  # Import tqdm for progress bar
from multiprocessing import Pool, cpu_count  # Import Pool for multiprocessing

def find_files(directory, valid_extensions, skip_extensions, skip_folders):
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

def process_file(file_info):
    """Read the content of a file and return its path and content."""
    file, base_directory, include_full_path = file_info
    if include_full_path:
        relative_path = file  # Use full path if requested
    else:
        relative_path = os.path.relpath(file, base_directory)  # Compute relative path

    with open(file, 'r', encoding='utf-8') as content_file:
        content = content_file.read()

    return (relative_path, content)

def create_summary_file(file_list, output_file, include_full_path, base_directory):
    """Create a summary file with the contents of each file."""
    with open(output_file, 'w') as f:
        for relative_path, content in tqdm(file_list, desc="Writing files", unit="file"):
            f.write(f"Path: {relative_path}\n")  # Include "Path: " in output
            f.write("=" * len(relative_path) + "\n")  # Separator line
            f.write(content + "\n")  # Write content of the file
            f.write("-------------------------------------------------\n\n")  # Separator for readability

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Find specified files in a directory.')
    parser.add_argument('directory', type=str, nargs='?', help='The directory to search in')
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

    args = parser.parse_args()

    # If no directory is provided, print usage information and exit
    if not args.directory:
        parser.print_help()
        return

    # Convert skip extensions and valid extensions from list of strings to tuples
    skip_extensions = tuple(args.skip) if args.skip else ()
    
    # Default valid extensions including Dart and Flutter related files
    valid_extensions = tuple(args.extensions) if args.extensions else (
        '.txt', '.py', '.c', '.cpp', '.js', '.java', 
        '.html', '.css', '.md', '.dart', '.yaml', 
        '.json'
    )

    # Get the list of folders to skip
    skip_folders = args.skip_folders if args.skip_folders else []

    # Find files in the specified directory
    found_files = find_files(args.directory, valid_extensions, skip_extensions, skip_folders)

    if found_files:
        # Prepare file information for processing
        file_info_list = [(file, args.directory, args.full_path) for file in found_files]

        # Use multiprocessing to process files concurrently
        with Pool(processes=cpu_count()) as pool:  # Use all available CPU cores
            results = pool.map(process_file, file_info_list)

        # Create summary file with found files' content
        create_summary_file(results, args.output, args.full_path, args.directory)
        print(f'Summary created: {args.output}')
    else:
        print('No matching files found.')

if __name__ == '__main__':
    main()
