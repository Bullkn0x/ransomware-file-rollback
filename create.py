from stage.sample_files import get_cli_args, prompt_user, create_sample_files, update_sample_files, path_is_safe, encrypt_directory_files,decrypt_directory_files
from dotenv import load_dotenv
import os
import colored
from cryptography.fernet import Fernet
from utils.helpers import generate_key

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

def initiate_cli():
    
    # Parse the command line arguments using the argparse module
    args = get_cli_args()
    print(args)
    # If no command-line arguments were provided, display a prompt to the user
    if not any([args.create, args.update, args.encrypt, args.decrypt]):
       prompt_user(args)
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





if __name__ == "__main__":
    initiate_cli()