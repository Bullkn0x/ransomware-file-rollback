from flask import Flask, render_template, request
import json
from stage.sample_files import create_sample_files, update_sample_files, path_is_safe,encrypt_directory_files,decrypt_directory_files
app = Flask(__name__)
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os

load_dotenv()
SAMPLE_FILE_DIR = os.environ.get('sample_file_directory')
SECRET = Fernet.generate_key()
@app.route("/")
def index():
    return render_template("wizard2.html")


@app.route('/process_actions', methods=['POST'])
def process_actions():
    actions_list = json.loads(request.data)
    
    for action in actions_list:
        if action['action_id'] == 1: # Create file action
            num_files = int(action['numFiles'])
            create_sample_files(num_files)
        if action['action_id'] == 2: # Update file content action
            update_sample_files()
        if action['action_id'] == 3: # Encrypt file content action
            if path_is_safe(SAMPLE_FILE_DIR):
                encrypt_directory_files(SAMPLE_FILE_DIR, SECRET)
        if action['action_id'] == 4: # Decrypt file content action
            if path_is_safe(SAMPLE_FILE_DIR):
                decrypt_directory_files(SAMPLE_FILE_DIR, SECRET)

    # Do something with the form data
    # print(json.dumps(data,indent=4))
    response = {'status': 'success'}
    return response

if __name__ == "__main__":
    app.run(host='127.0.0.1',debug=True, port=8000)