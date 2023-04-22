from stage.sample_files import get_cli_args, prompt_user, create_sample_files, update_sample_files, path_is_safe, encrypt_directory_files,decrypt_directory_files
from dotenv import load_dotenv
import os
import colored
from cryptography.fernet import Fernet

load_dotenv()
SAMPLE_FILE_DIR = os.environ.get('sample_file_directory')
SECRET = os.environ.get('SECRET_KEY').encode('utf-8')
print(SECRET)
def initiate_cli():
    
    # Parse the command line arguments using the argparse module
    args = get_cli_args()
    # If no command-line arguments were provided, display a prompt to the user
    if not any([args.create, args.update, args.encrypt, args.decrypt]):
       prompt_user()
    else:
        if args.create:
            create_sample_files(args.create,args.directory)
        if args.update:
            update_sample_files(args.directory)

        if args.encrypt:
            if path_is_safe(args.directory):
                encrypt_directory_files(SECRET,args.directory)
        if args.decrypt:
            if path_is_safe(args.directory):
                decrypt_directory_files(SECRET,args.directory)





if __name__ == "__main__":
    initiate_cli()