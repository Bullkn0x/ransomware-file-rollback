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
 


# Load vars from env
load_dotenv()
config_path = os.getenv('config_file_path')
admin_id = os.getenv('admin_id')
EVENT_TYPES_TO_QUERY = ['UPLOAD','EDIT','DELETE','UNDELETE']
USER_TO_QUERY = os.getenv('user_to_query')
START_TIME_WINDOW = os.getenv('start_window')
END_TIME_WINDOW = os.getenv('end_window')


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
    
    stream_position = 0
    events = sa_client.events().get_admin_events(
        # stream_type=EnterpriseEventsStreamType.ADMIN_LOGS, 
        created_after=START_TIME_WINDOW,
        created_before=END_TIME_WINDOW,
        stream_position=stream_position,
        event_types=EVENT_TYPES_TO_QUERY
        )
    stream_position = events['next_stream_position']

    file_dict = {}
    with open('ransomware_files.csv','w') as out_file:
        writer = csv.writer(out_file)
        headers = ['Created By Email','Created By User ID','Event Type','Item Type','Item Name','Item ID','Timestamp']
        writer.writerow(headers)
        for event in events['entries']:
            event_type = event.event_type
            event_user_email = event.created_by.login
            event_user_id = event.created_by.id
            event_time = event.created_at

            if event_user_email == USER_TO_QUERY and event_type in EVENT_TYPES_TO_QUERY:

                item_type = event.source['item_type']
                item_name = event.source['item_name']
                item_id = event.source['item_id']

                if item_type == 'file':
                    #write event details to csv
                    writer.writerow([event_user_email,event_user_id,event_type,item_type,item_name,item_id,event_time])
                    
                    #lookup previos versions for file using user client

                    if item_id not in file_dict:  #UPLOAD occurred
                        file_dict[item_id] = {
                            'file_id':item_id,
                            'event_created_by_user_id': event_user_id,
                            'event_created_by_login': event_user_email,
                            'item_type': item_type,
                            'item_name': item_name,
                            'events': [{'event_type': event_type,'event_time':event_time}],
                            'previous_versions':[]
                        }

                    else:
                        file_dict[item_id]['events'].append({'event_type': event_type,'event_time':event_time})
                    
                    



                    
                    
                    # print(f'Got {event_type} |{item_type} {item_name} - {item_id} | by ({event_user_email}-{event_user_id}) | {event_time}')

    with open('result.json', 'w') as fp:
        json.dump(file_dict, fp, indent=4)


    #GET FILE VERSIONS
    for item_id, item_details in file_dict.items():
        #RESTORE TRASHED FILE AND ADD TO ORIGINAL FILE MAP DETAILS

        #if item was trashed and the last event was TRASHING, restore the file first and use new file ID
        if item_details['events'][-1]['event_type'] == 'DELETE':
            file_to_restore = user_client.file(file_id=item_id)
            restored_file = user_client.trash().restore_item(file_to_restore)
            print(f'File ID is {restored_file.id} and name is {restored_file.name}')
            file_dict[item_id]['restored_file_id'] = restored_file.id 

        if 'restored_file_id' in item_details:
            item_id = item_details['restored_file_id']
        
        file_versions = user_client.file(item_id).get_previous_versions()
        for version in file_versions:
            item_details['previous_versions'].append({
                'version_id':version.id,
                'version_name':version.name,
                'created_at':version.created_at
            })
            print(f'{version.name} | File version {version.id} was created at {version.created_at}')
        print('-'*100)

    with open('result.json', 'w') as fp:
        json.dump(file_dict, fp, indent=4)
    ######## Restore Previous File version
    

######## pretty print ########
def pretty_dict(in_dict):
    print(json.dumps(in_dict,indent=4))
    return
    
################# Load config file ############
def load_config(file_path):
    with open(file_path) as file:
        return json.load(file)
    



    
if __name__ == "__main__":
    main()