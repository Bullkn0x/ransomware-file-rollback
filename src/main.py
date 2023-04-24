from .models.box import BoxAPI
from .models.logger import Logger
from .utils.helpers import write_json_file, read_json_file, get_date_object, get_date_string,get_sample_directory_file_paths, get_cli_args, process_args
from .utils.box_helpers import filter_user_events, get_event_type
from web.app import app, socketio
import json 
from datetime import datetime, timezone
import csv
import json 
import os
from dotenv import load_dotenv
from json import JSONEncoder
from boxsdk.exception import BoxAPIException
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
import colored
import time
import boto3
# Load environment variables
load_dotenv()
config_path = os.getenv('config_file_path')   # Path to the Box API config file
admin_id = os.getenv('admin_id')               # Admin user ID
EVENT_TYPES_TO_QUERY = ['UPLOAD','EDIT','DELETE','UNDELETE','MOVE']  # Box event types to query
USER_TO_QUERY = os.getenv('user_to_query')     # User email to filter events
START_TIME_WINDOW = os.getenv('start_window')  # Start time window to query events
END_TIME_WINDOW = os.getenv('end_window')      # End time window to query events
BOX_SAMPLE_FOLDER_ID = os.getenv('BOX_SAMPLE_FOLDER_ID')
LOCAL_SAMPLE_FILE_DIR = os.environ.get('local_sample_file_directory')

def main():
    """
    Retrieves and processes events from the Box API event stream, gathering all previous
    versions of the file, and restoring the latest version prior to the start window. 
    Presumably the "START_TIME_WINDOW" denotes the beginning of a malware attack, so by 
    promoting the version just prior, the file is restored to its intended state.
    """
    

    args = get_cli_args()
    if args.web:
        socketio.run(app,host='127.0.0.1',port="8000",debug=True)


    process_args(args)
    # initiate_cli()
    
    # Create Box API client
    exit()
    box_api = BoxAPI(config_path, admin_id)

    # Initiailize a user client for performing various file related tasks 
    user = box_api.sa_client.user().get()
    admin_user = box_api.sa_client.user(user_id=admin_id)
    admin_client = box_api.sa_client.as_user(admin_user)


    #create app users for handling large workloads
    box_api.delete_users_with_threads('ransomasdfware',20)

    app_users= box_api.create_users_with_threads('ransomasdfware',10,30)
    app_user_group = box_api.create_group('ransom_app_user_group')
    box_api.add_users_to_group_with_threads(app_users, app_user_group, admin_client)
    
    box_api.add_group_collaboration(BOX_SAMPLE_FOLDER_ID, app_user_group,'co-owner',admin_client)

    sample_file_paths = get_sample_directory_file_paths(LOCAL_SAMPLE_FILE_DIR)
    
    start_time = time.time()
    box_api.upload_files_with_threads(BOX_SAMPLE_FOLDER_ID, sample_file_paths, app_users, 200)
    total_time = time.time() - start_time
    print(f"Total Upload execution time: {total_time} seconds")
    box_api.delete_users_with_threads('ransomasdfware',20)

    exit()


    
    # Get events from Box API Event Stream
    events = box_api.get_admin_events(START_TIME_WINDOW, END_TIME_WINDOW,EVENT_TYPES_TO_QUERY)
    
    # If no events are found, nothing to process
    if not events:
        return
    
    # Filter events by user, event type, and item type (file)
    file_dict = filter_user_events(events=events, 
                                   user_email=USER_TO_QUERY,
                                   event_types=EVENT_TYPES_TO_QUERY,
                                   item_types=['file'])
    write_json_file('outputs/user_file_events.json', file_dict)   


    # Get file versions for the filtered files
    user_files_with_versions= box_api.batch_get_file_versions(file_dict.items(), user_client)
    write_json_file('outputs/user_file_events.json', user_files_with_versions)   
    


if __name__ == "__main__":
    main()