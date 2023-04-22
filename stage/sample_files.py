import os
import argparse
import datetime
from dotenv import load_dotenv, dotenv_values
from cryptography.fernet import Fernet
import base64
from colored import fg, bg, attr


load_dotenv()

SAMPLE_FILE_DIR = os.environ.get('sample_file_directory')

def create_sample_files(num_files, directory=SAMPLE_FILE_DIR):
    """
    Create sample files with arbitrary content in the specified directory.

    Args:
        directory (str): The directory path where the sample files will be created.
        num_files (int): The number of sample files to create.

    Returns:
        None
    """
    for i in range(1, num_files+1):
        # Generate a timestamp string
        now = datetime.datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d_%H:%M:%S%p')

        # Construct a unique filename with a timestamp
        file_name = f"sample_file_{i}-{timestamp_str}.txt"
        file_path = os.path.join(directory, file_name)

        # Write some arbitrary content to the file
        with open(file_path, "w") as f:
            f.write(f"This is sample file {i}.\nIt contains some arbitrary content. {timestamp_str}")
            
        print(f"{fg('green')}Created sample file {i} at {file_path}.{attr('reset')}")

def update_sample_files(directory=SAMPLE_FILE_DIR):
    """
    Update the contents of all sample files in the specified directory.

    Args:
        directory (str): The directory path containing the sample files.

    Returns:
        None
    """
    # Get the current timestamp
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Loop through each file in the directory and update its content
    for file_name in os.listdir(directory):
        if file_name.startswith("sample_file") and file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            with open(file_path, "a") as f:
                f.write(f"\n\nFile updated on {timestamp}.")
            print(f"{fg('green')}Updated {file_name} with new content appended:\n\t{attr('reset')}File updated on {timestamp}.")


def prompt_user():
    """
    Prompt the user to choose between creating new sample files, updating existing ones, encrypting files, or decrypting files.

    Returns:
        None
    """
    while True:
        print(f"{fg('orchid')}Welcome to the file creator/update wizard!{attr('reset')}")
        choice = input(f"{fg('magenta')}Would you like to create new files, update existing files, encrypt files, or decrypt files? (c/u/enc/dec): {attr('reset')}")
        if choice.lower() == 'c':
            num_files = int(input(f"{fg('yellow')}How many files would you like to create? {attr('reset')}"))
            create_sample_files(num_files)
        elif choice.lower() == 'u':
            update_sample_files()
        elif choice.lower() == 'enc':
            encrypt_directory_files(SAMPLE_FILE_DIR, SECRET)
        elif choice.lower() == 'dec':
            decrypt_directory_files(SAMPLE_FILE_DIR, SECRET)
        else:
            print("Invalid choice. Please enter 'c', 'u', 'enc', or 'dec'.")
            continue

        another_choice = input(f"{fg('magenta')}Would you like to run another command? (y/n): {attr('reset')}")
        if another_choice.lower() == 'y':
            continue
        elif another_choice.lower() == 'n':
            break
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")
            break

def get_cli_args():
    parser = argparse.ArgumentParser(description="Create sample files with arbitrary content.")
    parser.add_argument("-c", "--create", metavar="num_files", type=int, help="create sample files with arbitrary content")
    parser.add_argument("-u", "--update", action="store_true", help="update the contents of all sample files")
    parser.add_argument("-enc", "--encrypt", action="store_true", help="encrypt the contents all sample files")
    parser.add_argument("-dec", "--decrypt", action="store_true", help="decrypt the contentsof all sample files")
    parser.add_argument("-dir", "--directory", metavar="path", default=SAMPLE_FILE_DIR, help="the directory where the sample files will be created or updated (default: current directory)")
    parser.add_argument("-w", "--wizard", metavar="wizard", help="If no arguments are present and the user would like to use an interactive CLI to service commands")
    args = parser.parse_args()

    return args
 
def path_is_safe(directory=SAMPLE_FILE_DIR):
    for root, dirs, files in os.walk(directory):
        if "test_files" in root:
            return True
    return False

def encrypt_file(filename, key):
    with open(filename, 'rb') as f:
        data = f.read()
    # generate a key
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(filename, 'wb') as f:
        f.write(encrypted)

def decrypt_file(filename, key):
    with open(filename, 'rb') as f:
        data = f.read()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)
    with open(filename, 'wb') as f:
        f.write(decrypted)

def encrypt_directory_files(key,directory=SAMPLE_FILE_DIR):
    if path_is_safe(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    data = f.read()
                if data.startswith(b'gAAAAA'):
                    print(f"\t{fg('yellow')}NO ACTION: File {filepath} is already encrypted.{attr('reset')}")
                else:
                    try:
                        encrypt_file(filepath, key)
                        print(f"\t{fg('green')}Encrypted file: {filepath}{attr('reset')}")
                    except Exception as e:
                        print(f'Failed to encrypt file: {filepath}, {e}')
               
def decrypt_directory_files(key,directory=SAMPLE_FILE_DIR):
    if path_is_safe(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    decrypt_file(filepath, key)
                    print(f"\t{fg('green')}Decrypted file: {filepath}{attr('reset')}")
                except Exception as e:
                    print(f'Failed to decrypt file: {filepath}, {e}')
if __name__ == "__main__":
    pass
