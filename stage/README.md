# File Creator and Updater

A Python script to create and update multiple files with arbitrary content.

## Installation

1. Clone the repository:

```git clone https://github.com/Bullkn0x/ransomware-file-rollback```


2. Install the required dependencies:

```pip install -r requirements.txt```

## Usage

The script can be used to create and update files. You can either provide the arguments via the command line or let the script guide you with an interactive wizard.

### Creating Files

To create new files, run the following command:

```python sample_files.py -c <number_of_files> -s <file_size> -o <output_directory>```

- `number_of_files`: Number of files to be created.
- `file_size`: Size of each file in bytes.
- `output_directory`: Directory where the files will be created.

### Updating Files

To update existing files, run the following command:

```python sample_files.py -u -o <output_directory>```

- `output_directory`: Directory where the files are located.

### Interactive Wizard

If you don't provide any arguments, the script will launch an interactive wizard to guide you through the process of creating or updating files. Use the arrow keys to navigate the menus, and press Enter to select options.

## License

This script is released under the [MIT License](https://opensource.org/licenses/MIT).