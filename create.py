from stage.sample_files import get_cli_args, prompt_user, path_is_safe, create_sample_files, update_sample_files,encrypt_directory_files,decrypt_directory_files
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()
SAMPLE_FILE_DIR = os.environ.get('sample_file_directory')
SECRET = os.environ.get('SECRET_KEY').encode('utf-8')
key = Fernet(SECRET)


def main():
    
    # Parse the command line arguments using the argparse module
    args = get_cli_args()
    # If no command-line arguments were provided, display a prompt to the user
    if not any([args.create, args.update, args.encrypt, args.decrypt]):
       prompt_user()
    else:
        if args.create:
            create_sample_files(args.create,SAMPLE_FILE_DIR)
        if args.update:
            update_sample_files(SAMPLE_FILE_DIR)

        if args.encrypt:
            if path_is_safe(SAMPLE_FILE_DIR):
                encrypt_directory_files(SAMPLE_FILE_DIR, SECRET)
        if args.decrypt:
            if path_is_safe(SAMPLE_FILE_DIR):
                decrypt_directory_files(SAMPLE_FILE_DIR, SECRET)




if __name__ == "__main__":
   

    main()