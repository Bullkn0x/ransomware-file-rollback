from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, emit
import json
from rollback.create import (
    create_sample_file,
    create_sample_files, 
    update_sample_files, 
    encrypt_directory_files, 
    decrypt_directory_files
)
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os
import datetime
import logging

import eventlet
eventlet.monkey_patch()

# Load environment variables
load_dotenv()
# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, debug=True)
SAMPLE_FILE_DIR = os.environ.get('box_drive_sample_file_directory')
SECRET = Fernet.generate_key()
LOG_FILE=os.path.join(app.static_folder, 'json', 'stage_logs.json')

# Initialize logging
log_file = os.path.join(app.static_folder, 'json', 'stage_logs.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

# Define routes
@app.route("/")
def index():
    log_file_path = os.path.join(app.static_folder, 'json', 'stage_logs.json')

    # Try to read logs from file, if file doesn't exist or is empty, return an empty list
    try:
        with open(log_file_path, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    # Pass logs to template
    return render_template("wizard2.html", logs=logs)

@app.route('/process_actions', methods=['POST'])
def process_actions():
     # Load actions from request data
    actions_list = json.loads(request.data)

    # Try to load logs from file, if file doesn't exist or is empty, initialize an empty list
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    # Loop through actions
    for action in actions_list:
        if action['action_id'] == 1: # Create file action
            num_files = int(action['numFiles'])
            process_create_files_action(num_files)

        if action['action_id'] == 2: # Update file content action
            process_update_files_action()

        if action['action_id'] == 3: # Encrypt file content action
            if path_is_safe(SAMPLE_FILE_DIR):
                encrypt_directory_files(SECRET)
        if action['action_id'] == 4: # Decrypt file content action
            if path_is_safe(SAMPLE_FILE_DIR):
                decrypt_directory_files(SECRET)

    response = {'status': 'success'}
    return response


# Socket Events 

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('clear_web_logs')
def handle_log():
    log_file = os.path.join(app.static_folder, 'json', 'stage_logs.json')

    with open(log_file, 'w') as f:
        f.write("[]")

    # Log the "Logs Cleared" event
    event_timestamp = datetime.datetime.now().strftime('%b %d, %Y %I:%M:%S %p')
    log_dict = {'title': 'Logs Cleared', 'time': event_timestamp, 'message': 'All logs have been cleared.'}
    logging.info(json.dumps(log_dict))

    # Emit success message to frontend
    emit('logs_cleared', {'status': 'success'})


def log_event(title, message):
    """
    Log an event and emit a log event to the client.

    Args:
        title (str): The title of the event.
        message (str): The message associated with the event.

    Returns:
        None
    """
    # Get the current timestamp
    now = datetime.datetime.now()
    event_timestamp = now.strftime('%b %d, %Y %I:%M:%S %p')

    # Create the log dictionary
    log_dict = {'title': title, 'time': event_timestamp, 'message': message}

    # Emit the log event to the client
    socketio.emit('log', log_dict)


    # Write the log event to the log file
    try:
        with open(LOG_FILE, 'r') as f:
            log_json = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_json = []
    log_json.append(log_dict)
    with open(LOG_FILE, 'w') as f:
        json.dump(log_json,f,indent=4)
        


def process_create_files_action(num_files):
    """
    Create sample files and log each file creation event.

    Args:
        num_files (int): The number of files to create.

    Returns:
        None
    """
    # Log the "Create Sample Files" event
    message = f'Create Sample Files initiated ({num_files} files being created)'
    log_event('Create Sample Files', message)

    # Create sample files and log each file creation event
    for i in range(1, num_files+1):
        file_details = create_sample_file(i)
        timestamp = datetime.datetime.now().strftime('%b %d, %Y %I:%M:%S %p')
        file_path = file_details['file_path']
        message = f'Created file at {file_path}'
        log_event('File Created', message)


def process_update_files_action():
    """
    Update the content of all sample files and log the event.

    Returns:
        None
    """
    # Log the "Update Sample Files" event
    message = 'Updating sample files'
    log_event('Update Sample Files initiated', message)

    # Update the content of all sample files
    update_sample_files()

    # Log the "Update Sample Files Completed" event
    message = 'Sample files updated'
    log_event('Update Sample Files Completed', message)


if __name__ == "__main__":
    # app.run(host='127.0.0.1',debug=True, port=8000,ssl_context=('cert.pem', 'key.pem'))
    socketio.run(app, port=8000, debug=True)
