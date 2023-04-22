from models.box import BoxAPI
from models.logger import Logger
from create import initiate_cli
import json 
from datetime import datetime, timezone
import csv
import json 
import os
from dotenv import load_dotenv
from json import JSONEncoder
from utils.helpers import write_json_file, read_json_file, get_date_object, get_date_string
from utils.box_helpers import filter_user_events, get_event_type
from boxsdk.exception import BoxAPIException
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
import colored

# Load environment variables
load_dotenv()
config_path = os.getenv('config_file_path')   # Path to the Box API config file
admin_id = os.getenv('admin_id')               # Admin user ID
EVENT_TYPES_TO_QUERY = ['UPLOAD','EDIT','DELETE','UNDELETE','MOVE']  # Box event types to query
USER_TO_QUERY = os.getenv('user_to_query')     # User email to filter events
START_TIME_WINDOW = os.getenv('start_window')  # Start time window to query events
END_TIME_WINDOW = os.getenv('end_window')      # End time window to query events

def main():
    """
    Retrieves and processes events from the Box API event stream, gathering all previous
    versions of the file, and restoring the latest version prior to the start window. 
    Presumably the "START_TIME_WINDOW" denotes the beginning of a malware attack, so by 
    promoting the version just prior, the file is restored to its intended state.
    """
    

    # Create Box API client
    box_api = BoxAPI(config_path, admin_id)

    # Initiailize a user client for performing various file related tasks 
    user = box_api.sa_client.user().get()
    admin_user = box_api.sa_client.user(user_id=admin_id)
    user_client = box_api.sa_client.as_user(admin_user)

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
   


if __name__ == "__main__":
    main()