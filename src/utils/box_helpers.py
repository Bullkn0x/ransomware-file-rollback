import csv

def filter_user_events(events, user_email, event_types, item_types):
    file_dict = {}
    with open('outputs/ransomware_files.csv', 'w') as out_file:
        writer = csv.writer(out_file)
        headers = ['Created By Email', 'Created By User ID', 'Event Type', 'Item Type', 'Item Name', 'Item ID', 'Timestamp']
        writer.writerow(headers)
        for event in events:
            event_type = event.event_type
            event_user_email = event.created_by.login
            event_user_id = event.created_by.id
            event_time = event.created_at

            if event_user_email == user_email and event_type in event_types:
                item_type = event.source['item_type']
                item_name = event.source['item_name']
                item_id = event.source['item_id']
                if item_type in item_types:
                    if item_type == 'file':
                        # Write event details to csv
                        writer.writerow([event_user_email, event_user_id, event_type, item_type, item_name, item_id, event_time])

                        # Lookup previous versions for file using user client
                        if item_id not in file_dict:  # UPLOAD occurred
                            file_dict[item_id] = {
                                'file_id': item_id,
                                'event_created_by_user_id': event_user_id,
                                'event_created_by_login': event_user_email,
                                'item_type': item_type,
                                'item_name': item_name,
                                'events': [{'event_type': event_type, 'event_time': event_time}],
                                'previous_versions': []
                            }

                        else:
                            file_dict[item_id]['events'].append({
                                'event_type': event_type, 
                                'event_time': event_time
                                })

    return file_dict

def get_event_type(item_details):
    return item_details['events'][-1]['event_type'] 

