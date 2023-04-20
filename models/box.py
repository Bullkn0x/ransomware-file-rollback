from boxsdk import Client
from boxsdk import JWTAuth
from boxsdk.exception import BoxAPIException
from boxsdk.object.events import EnterpriseEventsStreamType
import os
import json
import logging 

class Logger:
    """
    A class for creating logger instances.

    Attributes:
    - name (str): The name of the logger instance.
    - level (int): The logging level for the logger instance.

    Methods:
    - get_logger(): Returns the logger instance.
    - get_error_logger(): Returns the error logger instance.
    """
    def __init__(self, name, level=logging.INFO):
        # Create a logger instance with the provided name and logging level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Set up formatter for log messages
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(funcName)s:%(message)s')

        # Set up file handler for writing log messages to a file
        file_handler = logging.FileHandler(f'logs/{name}.log')
        file_handler.setFormatter(formatter)

        # Set up stream handler for writing log messages to the console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Add the file handler and stream handler to the logger instance
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        # Set up an error logger instance
        self.error_logger = logging.getLogger(f'{name}_errors')
        self.error_logger.setLevel(logging.ERROR)

        # Set up formatter for error messages
        error_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        # Set up file handler for writing error messages to a file
        error_file_handler = logging.FileHandler(f'logs/{name}_errors.log')
        error_file_handler.setFormatter(error_formatter)
        
        # Add the file handler to the error logger instance
        self.error_logger.addHandler(error_file_handler)


    def get_logger(self):
        return self.logger

    def get_error_logger(self):
        return self.error_logger

class BoxAPI(Logger):
    def __init__(self, config_path, admin_id):
        """
        Initializes a Box API client instance with the provided admin ID and configuration file path.

        Args:
        - config_path (str): The file path to the JSON configuration file containing Box API authentication settings.
        - admin_id (str): The ID of the Box admin user to authenticate as.

        Returns:
        - None
        """
        super().__init__('box_api')


        self.config_path = config_path
        self.admin_id = admin_id
        self.sa_client = self.authenticate()
        
   
        self.logger.info(f'Box Client Initialized with admin id:{self.admin_id}')
    
    def authenticate(self):
        """
        Authenticates the Box API client instance using the provided configuration settings.

        Args:
        - None

        Returns:
        - sa_client (boxsdk.Client): A Box API client instance authenticated with the provided configuration settings.
        """

        if not os.path.exists(self.config_path):
            print('no config.json file present, try again')
            self.error_logger.error('Config.json file not found.')

            return None

        app_config = self.load_config(self.config_path)

        # Setup authorization using config.json file
        auth = JWTAuth.from_settings_dictionary(app_config)
        auth.authenticate_instance()

        # Create Box API client
        sa_client = Client(auth)
        return sa_client

    def load_config(self, file_path):
        with open(file_path) as file:
            return json.load(file)

    def get_admin_events(self, start_time, end_time,event_types):
        """
        Retrieves Box events created between the specified start and end times for the specified event types.

        Args:
        - start_time (str): The start time (in ISO format) for the event search window.
        - end_time (str): The end time (in ISO format) for the event search window.
        - event_types (list): A list of strings representing the types of Box events to retrieve.

        Returns:
        - events (list): A list of Box events retrieved for the specified search window and event types.
        """

        if not self.sa_client:
            self.logger.error('Box API client not initialized. get_admin_events() stopped')

            return None

        # Initialize stream_position and events list
        stream_position = None
        events = []

        # Loop to retrieve events in chunks of 500
        while True:
            event_stream = self.sa_client.events().get_admin_events(
                event_types=event_types,
                created_after=start_time,
                created_before=end_time,
                stream_position=stream_position,
                limit=1000
            )

            # Extend events list with new entries
            events.extend(event_stream['entries'])
            
            # Update stream_position for next chunk and break loop if end of stream is reached
            stream_position = event_stream['next_stream_position']
            if not stream_position or event_stream['chunk_size'] == 0:
                break
        
        # Log number of events retrieved
        self.logger.info(f'{len(events)} events retrieved from {start_time} to {end_time} with event types {event_types}.')

        return events

    def get_file_versions(self, file_id, user_client):
        """
        Retrieves the previous versions of the specified Box file.

        Args:
        - file_id (str): The ID of the Box file to retrieve previous versions for.
        - user_client (boxsdk.Client): A Box API client instance authenticated as a user with access to the specified file.

        Returns:
        - versions (list): A list of dictionaries representing the previous versions of the specified Box file, including version ID, version name, and creation date/time.
        """

        try:
            file_versions = user_client.file(file_id).get_previous_versions()
        except BoxAPIException as e:
            self.error_logger.error(f'Error retrieving file versions for file ID {file_id}.  File Likely Trashed outside past end of time window specified Error message: {e.status}')
            pass

        versions = []
        for version in file_versions:
            versions.append({
                'version_id':version.id,
                'version_name':version.name,
                'created_at':version.created_at
            })
            print(f'{version.name} | File version {version.id} was created at {version.created_at}')
            self.logger.info(f'{version.name} | File version {version.id} was created at {version.created_at}')
        print('-'*100)
        self.logger.info(f'{len(versions)} versions retrieved for file ID {file_id}.')
        return versions

    def batch_get_file_versions(self, files, user_client):
        """
        Retrieves previous versions for multiple Box files in batch.

        Args:
        - files (list): A list of tuples, each containing a Box file ID and a dictionary of metadata for the file, including events and other information.
        - user_client (boxsdk.Client): A Box API client instance authenticated as a user with access to the specified files.

        Returns:
        - file_versions (list): A list of dictionaries representing the previous versions of the specified Box files, including file ID, file name, and a list of previous versions for each file.
        """


        file_versions = []

        # Iterate over the list of files and their metadata
        for item_id, item_details  in files:
            self.logger.info('-'*100)
            self.logger.info(f'Retrieving versions for item_id:{item_id} ')
            self.logger.info('-'*45)

            # Check if the file has been deleted last
            if item_details['events'][-1]['event_type']  == 'DELETE':
                
                # If the file has been deleted, restore it and save the restored file's ID
                try:
                    restored_file = self.restore_file(item_id, user_client)
                except BoxAPIException:
                    continue
                finally:
                    if not restored_file:
                        continue
                    
                item_details[item_id]['restored_file_id'] = restored_file.id
             
                if 'restored_file_id' in item_details:
                    item_details['file_id'] = item_details['restored_file_id']
                    print(f'item id:{item_id} restored_file_id {restored_file.id }')
               

            # Get the previous versions of the file
            try:
                item_id = item_details['file_id']
                versions = self.get_file_versions(item_id , user_client)
            except BoxAPIException as e:
                # If there is an error retrieving the file versions, log the error and continue to the next file
                self.error_logger.error(f'Error retrieving file versions for file ID {item_id}. File Likely Trashed outside past end of time window specified Error message: {e}')
                continue

            # If there are previous versions, add them to the file's metadata and append the metadata to the list of file versions
            if versions:
                item_details['previous_versions'] = versions
                file_versions.append(item_details)
            self.logger.info(f'Versions retried for item id:{item_id} | Number of versions: {len(versions)}')

        return file_versions

    def restore_file(self, file_id, user_client):
        """
        Restores a deleted Box file.

        Args:
        - file_id (str): The ID of the deleted Box file to restore.
        - user_client (boxsdk.Client): A Box API client instance authenticated as a user with access to the specified file.

        Returns:
        - restored_file (boxsdk.object.file.File): A Box API object representing the restored Box file.
        """
        
        try:
            file_to_restore = user_client.file(file_id)
            restored_file = user_client.trash().restore_item(file_to_restore)

        except BoxAPIException as e:
            print(e.status)
            if e.status == 403:
                self.error_logger.error(f'Error restoring file with ID {file_id}. File might be untrashed outside of end window. Error message: {e}')
            if e.status == 404:
                self.error_logger.error(f'Error restoring file with ID {file_id}. File Doesn\'t exist.  Error message: {e}')
            return None
        # print(f'File ID restored is {restored_file.id} and name is {restored_file.name}')
        return restored_file
        
