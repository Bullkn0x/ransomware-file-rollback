import os
import argparse
import datetime
from dotenv import load_dotenv, dotenv_values
from cryptography.fernet import Fernet
import base64
from colored import fg, bg, attr
from bullet import Bullet, YesNo, Input, colors
import sys
from termcolor import colored
from art import text2art

load_dotenv()

BOX_SAMPLE_FILE_DIR = os.environ.get('box_drive_sample_file_directory')
LOCAL_SAMPLE_FILE_DIR = os.environ.get('local_sample_file_directory')
ENCRYPTION_SECRET = os.environ.get('ENCRYPTION_SECRET_KEY')  # MUST be 32 byte url safe elligible

def create_sample_file(file_num, directory=LOCAL_SAMPLE_FILE_DIR):
    """
    Create a sample file with arbitrary content in the specified directory.

    Args:
        directory (str): The directory path where the sample file will be created.

    Returns:
        A dictionary containing details of the created file.
    """
    # Generate a timestamp string
    now = datetime.datetime.now()
    timestamp_str = now.strftime('%Y-%m-%d_%H:%M:%S%p')

    # Construct a unique filename with a timestamp
    file_name = f"sample_file_{file_num}{timestamp_str}.txt"
    file_path = os.path.join(directory, file_name)

    # Write some arbitrary content to the file
    with open(file_path, "w") as f:
        f.write(f"This is a sample file.\nIt contains some arbitrary content. {timestamp_str}")

    # Add file details to dictionary
    file_details = {'file_name': file_name, 'file_path': file_path, 'timestamp': timestamp_str}

    print(f"{fg('green')}Created sample file at {file_path}.{attr('reset')}")

    return file_details


def create_sample_files(num_files, directory=LOCAL_SAMPLE_FILE_DIR):
    """
    Create sample files with arbitrary content in the specified directory.

    Args:
        directory (str): The directory path where the sample files will be created.
        num_files (int): The number of sample files to create.

    Returns:
        A list of dictionaries containing details of the created files.
    """
    files = []
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
            
        # Add file details to list
        file_details = {'name': file_name, 'path': file_path, 'timestamp': timestamp_str}
        files.append(file_details)
        
        print(f"{fg('green')}Created sample file {i} at {file_path}.{attr('reset')}")
    
    return files

def update_sample_files(directory=LOCAL_SAMPLE_FILE_DIR):
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

def encrypt_directory_files(key,directory=LOCAL_SAMPLE_FILE_DIR):
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
               
def decrypt_directory_files(key,directory=LOCAL_SAMPLE_FILE_DIR):
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
