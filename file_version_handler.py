from boxsdk import Client
from boxsdk import JWTAuth
from boxsdk.object.collaboration import CollaborationRole
from boxsdk.exception import BoxAPIException
from boxsdk.object.events import EnterpriseEventsStreamType

from datetime import datetime, timezone
import csv
import json 
import os
from dotenv import load_dotenv
from json import JSONEncoder
import datetime as dt
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object





# Load vars from env
load_dotenv()
config_path = os.getenv('config_file_path')
admin_id = os.getenv('admin_id')
EVENT_TYPES_TO_QUERY = ['UPLOAD','EDIT']
USER_TO_QUERY = os.getenv('user_to_query')
START_TIME_WINDOW = os.getenv('start_window')
END_TIME_WINDOW = os.getenv('end_window')

def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)


def main():
    if not os.path.exists(config_path):
        print('no config.json file present, try again')

    app_config =load_config(config_path)

    # Setup authorization using config.json file
    auth = JWTAuth.from_settings_dictionary(app_config)
    auth.authenticate_instance()


    # Create Box API client
    sa_client = Client(auth)
    user = sa_client.user().get()
    admin_user = sa_client.user(user_id=admin_id)  
    user_client = sa_client.as_user(admin_user)

    #FILE VERSION FIND PREVIOUS
    ransomware_start_date = get_date_object(START_TIME_WINDOW)

    with open('outputs/user_file_events.json') as json_file:
        compromised_files = json.load(json_file)
        for file_details in compromised_files:
            file_id = file_details['file_id']
            lowest_found_time_diff = float('inf')
            closest_version_id = None
            previous_versions = file_details['previous_versions']
            for version in previous_versions:
                date_version_timestamp = get_date_object(version['created_at'])
                version_diff_from_attack = (ransomware_start_date - date_version_timestamp).total_seconds()
                if version_diff_from_attack < lowest_found_time_diff:
                    lowest_found_time_diff = version_diff_from_attack
                    closest_version_id = version['version_id']

            print(f'File: {file_details["item_name"]}  |  Closest Version {closest_version_id}  | Time Difference: {lowest_found_time_diff}s')
            version_to_promote = sa_client.file_version(closest_version_id)
            new_version = user_client.file(file_id).promote_version(version_to_promote)
            print(f'Version {closest_version_id} promoted; new version {new_version.id} created')

################# Load config file ############
def load_config(file_path):
    with open(file_path) as file:
        return json.load(file)

    
if __name__ == "__main__":
    main()