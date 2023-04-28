import json
import datetime as dt
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
from cryptography.fernet import Fernet
import os
import argparse
from .prompt import *
from ..create import create_sample_files, update_sample_files, encrypt_directory_files, decrypt_directory_files

BOX_SAMPLE_FILE_DIR = os.environ.get('box_drive_sample_file_directory')
LOCAL_SAMPLE_FILE_DIR = os.environ.get('local_sample_file_directory')
BOX_BASE_FOLDER_ID = os.environ.get('local_sample_file_directory')

ENV_CHOICES = {'local': 0, 'box-drive': 1, 'box-api': 2}
ENV_PATHS =  {'local': LOCAL_SAMPLE_FILE_DIR, 'box-drive': BOX_SAMPLE_FILE_DIR, 'box-api': BOX_BASE_FOLDER_ID}

ENCRYPTION_SECRET = os.environ.get('ENCRYPTION_SECRET_KEY')  # MUST be 32 byte url safe elligible
def generate_key():
    key = Fernet.generate_key()
    with open(".env", "a") as f:
        f.write(f'ENCRYPTION_SECRET_KEY="{key.decode("utf-8")}"')
    return key
if not ENCRYPTION_SECRET:
    try:
        key = generate_key()
        print("Generated new key and saved to .env")
    except Exception as e:
        print("Error generating new key:", e)
else:
    key = ENCRYPTION_SECRET.encode('utf-8')


def read_json_file(filepath):
    """
    Reads JSON data from a file and returns a Python dictionary.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data

def write_json_file(filepath, data):
    """
    Writes Python dictionary to a JSON file.
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def pretty_print_json(data):
    """
    Returns a pretty-printed JSON string from a Python dictionary.
    """
    return json.dumps(data, indent=4)

def create_json_file(filepath, data):
    """
    Creates a new JSON file and writes Python dictionary data to it.
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def flatten_json(json_data, parent_key='', sep='_'):
    items = []
    for key, value in json_data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def merge_json(json1, json2):
    merged = json1.copy()
    merged.update(json2)
    return merged

def path_is_safe(directory=LOCAL_SAMPLE_FILE_DIR):
    for root, dirs, files in os.walk(directory):
        if "test_files" in root or "fake" in root:
            return True
    return False

def get_sample_directory_file_paths(directory):
    file_paths = []
    for file_name in os.listdir(directory):
        if file_name.startswith("sample_file") and file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            file_paths.append(file_path)

    return file_paths
            
def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)



def get_cli_args():
    parser = argparse.ArgumentParser(description="Create sample files with arbitrary content.")
    
    parser.add_argument("-env","--environment", choices=ENV_CHOICES.keys(), help='select environment to perform actions')
    
    

    parser.add_argument("-c", "--create", metavar="num_files", type=int, help="create sample files with arbitrary content")
    parser.add_argument("-u", "--update", action="store_true", help="update the contents of all sample files")
    parser.add_argument("-enc", "--encrypt", action="store_true", help="encrypt the contents all sample files")
    parser.add_argument("-dec", "--decrypt", action="store_true", help="decrypt the contentsof all sample files")
    parser.add_argument("-dir", "--directory", metavar="path", default=LOCAL_SAMPLE_FILE_DIR, help="the directory where the sample files will be created or updated (default: current directory)")
    parser.add_argument("-w", "--wizard", metavar="wizard", help="If no arguments are present and the user would like to use an interactive CLI to service commands")
    parser.add_argument("--app_user_prefix", metavar="prefix", default="", help="a prefix string to be attached to app users")
    parser.add_argument("--web", action="store_true", help="launches the web server to interact with the gui")
    
    args = parser.parse_args()
    

    return args

def perform_action_choice(choice_id, environment_file_path):
    if choice_id == 0:
        num_files = prompt_num_files()
        create_sample_files(int(num_files))
    elif choice_id == 1:
        update_sample_files()
    elif choice_id == 2:
        confirm_encryption = prompt_confirm_encryption()
        if confirm_encryption:
            encrypt_directory_files(key, environment_file_path)
        else:
            print(colored("Encryption cancelled.", "red"))
    elif choice_id == 3:
        confirm_decryption =  prompt_confirm_decryption()
        if confirm_decryption:
            decrypt_directory_files(key, environment_file_path)
        else:
            print(colored("Decryption cancelled.", "red"))
    else:
        print(colored("Invalid choice. Please try again.", "red"))


def process_args(args):
    
    print(args)
    if not args.environment:
        environment_name, environment_id = prompt_environment()
        environment_path = ENV_PATHS[environment_name]
    else:
        environment_name = args.environment
        environment_id = ENV_CHOICES[environment_name]
    
    environment_path = ENV_PATHS[environment_name]
    
    display_welcome_art(environment_name)

    # If no command-line action arguments were provided, prompt the user
    if not any([args.create, args.update, args.encrypt, args.decrypt]):
       action_name, action_id = prompt_user_action(args)
       perform_action_choice(action_id, environment_path)
    else:
        if args.create:
            create_sample_files(args.create,args.directory)
        if args.update:
            update_sample_files(args.directory)
        if args.encrypt:
            if path_is_safe(args.directory):
                encrypt_directory_files(key, args.directory)
        if args.decrypt:
            if path_is_safe(args.directory):
                decrypt_directory_files(key, args.directory)
