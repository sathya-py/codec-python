**Code Collator**

This Python application helps you find and summarize code files within a specified directory. It can handle various file extensions, skip specific folders and extensions, and create a summary report with file paths and content (optional).

**Features:**

- Finds files based on user-defined extensions (e.g., `.txt`, `.py`, `.java`).
- Allows skipping specific extensions and folders.
- Generates a summary report with file paths and content (optional).
- Utilizes multi-processing for faster execution (optional).

**Installation**

**Prerequisites:**

- Python 3 ([https://www.python.org/downloads/](https://www.google.com/url?sa=E&source=gmail&q=https://www.python.org/downloads/)))

**Instructions:**

1.  Save the code as a Python file named `codec2.py`.

2.  Open a terminal or command prompt and navigate to the directory containing the script (`codec2.py`).

3.  Run the application using the following command:

    ```bash
    python codec2.py <directory> [options]
    ```

    Replace `<directory>` with the path to the directory you want to search.

**Options:**

- `-o`, `--output`: Specify the output summary file name (default: summary.txt).
- `-s`, `--skip`: List of file extensions to skip (e.g., `-s ".jpg .png"`).
- `-e`, `--extensions`: List of valid extensions to include (default: includes common code extensions).
- `--full-path`: Include full file paths in the output.
- `--skip-folders`: List of folder names to skip (e.g., `--skip-folders "node_modules .git"`).

**Example Usage:**

```bash
python codec2.py ./my_code -o code_summary.txt -s ".md .html" --full-path
```

This command will search for files with extensions `.txt`, `.py`, `.c`, `.cpp`, etc. (excluding `.md` and `.html`) within the `./my_code` directory, create a summary report named `code_summary.txt`, and include full file paths in the output.

**Multiprocessing Note:**

While the application supports multi-processing for faster execution, it's currently disabled by default. To enable it, uncomment the line `with Pool(processes=cpu_count()) as pool:` in the `main` function. However, keep in mind that multi-processing might not always be beneficial for smaller datasets.

**Contributing**

We welcome contributions to this project\! Feel free to fork the repository, make changes, and submit pull requests.

**License**

This project is licensed under the MIT License. See the LICENSE file for details.
