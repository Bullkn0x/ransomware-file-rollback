from art import text2art
import colored
from bullet import Bullet
from colored import fg, bg, attr
from bullet import Bullet, YesNo, Input, colors
import sys
from termcolor import colored
from art import text2art
import os


BOX_SAMPLE_FILE_DIR = os.environ.get('box_drive_sample_file_directory')
LOCAL_SAMPLE_FILE_DIR = os.environ.get('local_sample_file_directory')
ENCRYPTION_SECRET = os.environ.get('ENCRYPTION_SECRET_KEY')  # MUST be 32 byte url safe elligible


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


def prompt_environment():
    return Bullet(
        prompt=colored("Do you want to perform the operation locally or via boxdrive?", "yellow"),
        choices=["local", "box-drive", "box-api"],
        return_index=True
    ).launch()

def prompt_user_action(args):
    # try:
    return Bullet(
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
    ).launch()
    #     action_choice_label, action_choice_id = cli_menu.launch()
    #     # perform_action_choice(action_choice_id, environment_file_path=SAMPLE_FILE_DIR)


    #     another_choice = Bullet(
    #         colored("Would you like to run another command?", "yellow") ,choices=['yes','no'],
    #     ).launch()
    #     if another_choice == 'yes':
    #         continue
    #     else:
    #         print("\nExiting program...")
    #         sys.exit(0)
    
    # except KeyboardInterrupt:
    #     print("\nExiting program...")
    #     sys.exit(0)

def prompt_confirm_encryption():
    return Bullet(
        colored("Are you sure you want to encrypt the files?", "yellow"),
        choices=['yes','no'],
    ).launch()

def prompt_confirm_decryption():
    return Bullet(
        colored("Are you sure you want to decrypt the files?", "yellow"),
        choices=['yes','no'],
    ).launch()

def prompt_num_files():
    return Input(
        colored("How many files would you like to create?", "yellow")
    ).launch()
