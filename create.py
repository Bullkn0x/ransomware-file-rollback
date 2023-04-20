from stage.sample_files import get_cli_args, prompt_user, create_sample_files, update_sample_files
from dotenv import load_dotenv
import os

load_dotenv()
SAMPLE_FILE_DIR = os.environ.get('sample_file_directory')

def main():
    
    # Parse the command line arguments using the argparse module
    args = get_cli_args()
    # If no command-line arguments were provided, display a prompt to the user
    if not args.create and not args.update:
       prompt_user()
    else:
        if args.create:
            create_sample_files(args.create,args.directory)
        if args.update:
            update_sample_files(args.directory)




if __name__ == "__main__":
   

    main()