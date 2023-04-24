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
if not ENCRYPTION_SECRET:
    try:
        key = generate_key()
        print("Generated new key and saved to .env")
    except Exception as e:
        print("Error generating new key:", e)
else:
    key = ENCRYPTION_SECRET.encode('utf-8')

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



def display_welcome_art(env):
    if env:
        title_art = text2art(f"File Wizard ({env})")
    else:
        title_art = text2art(f"File Wizard")
        
    print(colored(title_art, "cyan"))
    print(colored("Welcome to the file creator/update wizard!", "magenta"))
    print()

"""
Prompt the user to choose between creating new sample files, updating existing ones, encrypting files, or decrypting files.

Returns:
    None
"""


def perform_action_choice(choice_id, environment_file_path):
    if choice_id == 0:
        num_files = Input(
            colored("How many files would you like to create?", "yellow")
        ).launch()
        create_sample_files(int(num_files))
    elif choice_id == 1:
        update_sample_files()
    elif choice_id == 2:
        confirm_encryption = Bullet(
            colored("Are you sure you want to encrypt the files?", "yellow"),choices=['yes','no'],
        ).launch()
        if confirm_encryption:
            encrypt_directory_files(key, environment_file_path)
        else:
            print(colored("Encryption cancelled.", "red"))
    elif choice_id == 3:
        confirm_decryption =  Bullet(
            colored("Are you sure you want to encrypt the files?", "yellow"),choices=['yes','no'],
        ).launch()
        if confirm_decryption:
            decrypt_directory_files(key, environment_file_path)
        else:
            print(colored("Decryption cancelled.", "red"))
    else:
        print(colored("Invalid choice. Please try again.", "red"))


def prompt_user(args):
    if hasattr(args, 'environment'):
        env = args.environment
        print(env)
    else:
        env = None     

    display_welcome_art(env)

    try:
        while True:
            if not env:
                local_or_box = Bullet(
                    prompt=colored("Do you want to perform the operation locally or via boxdrive?", "yellow"),
                    choices=[
                        "Local",
                        "Box Drive",
                        "Box API"
                    ],
                    return_index=True
                )
                env = local_or_box.launch()

            if "Local" in env:
                SAMPLE_FILE_DIR = LOCAL_SAMPLE_FILE_DIR
                print(colored("Performing the operation locally... Path is set to:", "green"),colored(SAMPLE_FILE_DIR,"yellow"))
                # Perform the operation locally
            elif "Box Drive" in env:
                SAMPLE_FILE_DIR = BOX_SAMPLE_FILE_DIR
                print(colored("Performing the operation in Box Drive Directory... Path is set to:", "green"),colored(SAMPLE_FILE_DIR,"yellow"))
                # Perform the operation in Box tenant
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                return

            print(colored("Welcome to the file creator/update wizard!", "magenta"))
            cli_menu = Bullet(
                prompt=colored("What would you like to do?", "yellow"),
                choices=[
                    "📄  Create new files",
                    "📝 Update existing files",
                    "🔐  Encrypt files",
                    "🔓  Decrypt files",
                ],
                background_on_switch = colors.background["blue"],
                word_color = colors.foreground["black"],
                word_on_switch = colors.foreground["white"],
                return_index = True
            )
            action_choice_label, action_choice_id = cli_menu.launch()
            perform_action_choice(action_choice_id, environment_file_path=SAMPLE_FILE_DIR)


            another_choice = Bullet(
                colored("Would you like to run another command?", "yellow") ,choices=['yes','no'],
            ).launch()
            if another_choice == 'yes':
                continue
            else:
                print("\nExiting program...")
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)

def get_cli_args():
    parser = argparse.ArgumentParser(description="Create sample files with arbitrary content.")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--local", action="store_true", help="use local file system")
    group.add_argument("--boxdrive", action="store_true", help="use Box Drive")
    

    parser.add_argument("-c", "--create", metavar="num_files", type=int, help="create sample files with arbitrary content")
    parser.add_argument("-u", "--update", action="store_true", help="update the contents of all sample files")
    parser.add_argument("-enc", "--encrypt", action="store_true", help="encrypt the contents all sample files")
    parser.add_argument("-dec", "--decrypt", action="store_true", help="decrypt the contentsof all sample files")
    parser.add_argument("-dir", "--directory", metavar="path", default=LOCAL_SAMPLE_FILE_DIR, help="the directory where the sample files will be created or updated (default: current directory)")
    parser.add_argument("-w", "--wizard", metavar="wizard", help="If no arguments are present and the user would like to use an interactive CLI to service commands")
    parser.add_argument("--app_user_prefix", metavar="prefix", default="", help="a prefix string to be attached to app users")

    args = parser.parse_args()
    if args.local:
        args.environment = 'Local'
        args.file_path = LOCAL_SAMPLE_FILE_DIR
    elif args.boxdrive:
        args.environment = 'Box Drive'
        args.file_path = BOX_SAMPLE_FILE_DIR

    return args
 
def path_is_safe(directory=LOCAL_SAMPLE_FILE_DIR):
    for root, dirs, files in os.walk(directory):
        if "test_files" in root or "fake" in root:
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

def encrypt_directory_files(key,directory=LOCAL_SAMPLE_FILE_DIR):
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
               
def decrypt_directory_files(key,directory=LOCAL_SAMPLE_FILE_DIR):
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
