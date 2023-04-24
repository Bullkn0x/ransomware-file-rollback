from boxsdk import Client
from boxsdk import JWTAuth
from boxsdk.exception import BoxAPIException
from boxsdk.object.events import EnterpriseEventsStreamType
from boxsdk.object.collaboration import CollaborationRole
from .logger import Logger
from concurrent.futures import ThreadPoolExecutor
import os
import json
import logging 
import random
import boto3

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


    def upload_file(self, folder_id, file_path, file_name, as_user_object):
        """
        Uploads a file to the specified Box folder.

        Args:
        - folder_id (str): The ID of the Box folder to upload the file to.
        - file_path (str): The local file path of the file to upload.
        - file_name (str): The name to give to the uploaded file in Box.
        - user_client (boxsdk.Client): A Box API client instance authenticated as a user with access to the specified folder.

        Returns:
        - file (boxsdk.object.file.File): A Box file object representing the newly uploaded file.
        """
        app_user = self.sa_client.user(user_id=as_user_object.id)
        app_user_client = self.sa_client.as_user(app_user)
        folder = app_user_client.folder(folder_id)
    
        try:
            uploaded_file = folder.upload(file_path, file_name)
            self.logger.info(f'File "{file_name}" (ID:{uploaded_file.id}) uploaded to folder "{uploaded_file.parent.name}" (ID:{uploaded_file.parent.id}) by user {as_user_object.name} (ID:{as_user_object.id}).')
            return uploaded_file
        except BoxAPIException as e:
            self.logger.warning(f'Error uploading file to folder {folder_id}. Error message: {e}')
            return None
        

    def random_string(self, length=5):
        import string
        """
        Generates a random string of the specified length.

        Args:
        - length (int, optional): The length of the string to generate. Defaults to 5.

        Returns:
        - random_string (str): The randomly generated string.
        """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def upload_files_with_threads(self, folder_id, file_paths, as_user_objects, num_threads=4):
        """
        Uploads multiple files to the specified Box folder, using multiple threads to improve performance.

        Args:
        - folder_id (str): The ID of the Box folder to upload the files to.
        - file_paths (list of str): The local file paths of the files to upload.
        - as_user_objects (list of boxsdk.object.user.User): A list of Box user objects representing the users to upload the files as.
        - num_threads (int, optional): The number of threads to use for file upload. Defaults to 4.

        Returns:
        - None
        """
        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit upload_file() function for each file to executor
            for i, file_path in enumerate(file_paths):
                file_name = f'sample_file_{i}_{self.random_string()} - 2023-04-24_06:20:10AM.txt.txt'
                as_user_object = random.choice(as_user_objects)
                executor.submit(self.upload_file, folder_id, file_path, file_name, as_user_object)

        self.logger.info(f'{len(file_paths)} files uploaded to folder {folder_id} using {num_threads} threads.')
    

    def delete_file(self, file_id):
        """
        Deletes the file with the given file ID.

        Args:
        - file_id (str): The ID of the file to delete.

        Returns:
        - None
        """
        file = self.sa_client.file(file_id=file_id).delete()
        self.logger.info(f'File "{file.name}" (ID: {file_id}) deleted.')
        
    def delete_files_with_threads(self, file_ids, num_threads=4):
        """
        Deletes multiple files with multiple threads.

        Args:
        - file_ids (list of str): The IDs of the files to delete.
        - num_threads (int, optional): The number of threads to use for file deletion. Defaults to 4.

        Returns:
        - None
        """
        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit delete_file() function for each file to executor
            for file_id in file_ids:
                executor.submit(self.delete_file, file_id)

        self.logger.info(f'{len(file_ids)} files deleted using {num_threads} threads.')

    def upload_file_with_lambda(self, session, folder_id, file_path, file_name, lambda_function_name):
        """
        Uploads a single file to the specified Box folder by invoking an AWS Lambda function.

        Args:
        - folder_id (str): The ID of the Box folder to upload the file to.
        - file_path (str): The local file path of the file to upload.
        - file_name (str): The name of the file to upload.
        - lambda_function_name (str): The name of the AWS Lambda function to invoke for file upload.

        Returns:
        - None
        """
        # Create a Boto3 Lambda client
        session = boto3.Session(
            aws_access_key_id='AKIA26ZJD2CNBRTIIM6I',
            aws_secret_access_key='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'
        )
        lambda_client = session.client('lambda',region_name='us-east-1')

        # Invoke the Lambda function for the file
        payload = {
            'folder_id': folder_id,
            'file_path': file_path,
            'file_name': file_name
        }
        res = lambda_client.invoke_async(FunctionName=lambda_function_name, InvokeArgs=json.dumps(payload))
        self.logger.info(res)
        print(res)
        self.logger.info(f'File "{file_name}" sent to Lambda function "{lambda_function_name}" for upload.')

    def upload_files_with_lambda_threaded(self, folder_id, file_paths, lambda_function_name, num_threads=4):
        """
        Uploads multiple files to the specified Box folder, using multiple threads to invoke an AWS Lambda function for each file.

        Args:
        - folder_id (str): The ID of the Box folder to upload the files to.
        - file_paths (list of str): The local file paths of the files to upload.
        - lambda_function_name (str): The name of the AWS Lambda function to invoke for file upload.
        - num_threads (int, optional): The number of threads to use for file upload. Defaults to 4.

        Returns:
        - None
        """
        session = boto3.Session(
            aws_access_key_id='AKIA26ZJD2CNBRTIIM6I',
            aws_secret_access_key='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'
        )
        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit upload_file_with_lambda() function for each file to executor
            for file_path in file_paths:
                file_name = f'sample_file_{self.random_string()} - 2023-04-24_06:20:10AM.txt'
                executor.submit(self.upload_file_with_lambda, session, folder_id, file_path, file_name, lambda_function_name)

        self.logger.info(f'{len(file_paths)} files uploaded to folder {folder_id} via AWS Lambda function using {num_threads} threads.')
    
    def upload_files_with_lambda(self, folder_id, file_paths, lambda_function_name):
        """
        Uploads multiple files to the specified Box folder by invoking an AWS Lambda function for each file.

        Args:
        - folder_id (str): The ID of the Box folder to upload the files to.
        - file_paths (list of str): The local file paths of the files to upload.
        - lambda_function_name (str): The name of the AWS Lambda function to invoke for file upload.

        Returns:
        - None
        """

        # Create a Boto3 Lambda client
        session = boto3.Session(
            aws_access_key_id='AKIA26ZJD2CNBRTIIM6I',
            aws_secret_access_key='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'
        )
        lambda_client = session.client('lambda',region_name='us-east-1')

        # Loop through the file paths and invoke the Lambda function for each file asynchronously
        for file_path in file_paths:
            file_name = f'sample_file_{self.random_string()} - 2023-04-24_06:20:10AM.txt'
            payload = {
                'folder_id': folder_id,
                'file_path': file_path,
                'file_name': file_name
            }
            lambda_client.invoke_async(FunctionName=lambda_function_name, InvokeArgs=json.dumps(payload))
            self.logger.info(f'File "{file_name}" sent to Lambda function "{lambda_function_name}" for upload.')
        
        self.logger.info(f'{len(file_paths)} files uploaded to folder {folder_id} via AWS Lambda function.')
    
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
        

    def create_user(self, name):
        """
        Creates a new Box user with the specified name.

        Args:
        - name (str): The name to use for the new Box user.

        Returns:
        - None
        """

        try:
            user = self.sa_client.create_user(name,login=None)
            self.logger.info(f'User {name} created with ID {user.id}.')
        except BoxAPIException as e:
            self.error_logger.error(f'Error creating user {name}. Error message: {e}')
            pass

    def create_users_with_threads(self, prefix, num_users, num_threads=4):
        """
        Creates multiple new Box users with the specified name prefix and number, using multithreading to improve performance.

        Args:
        - prefix (str): The prefix to use for the new Box users.
        - num_users (int): The number of new Box users to create.
        - num_threads (int, optional): The number of threads to use for user creation. Defaults to 4.

        Returns:
        - A list of dictionaries containing the IDs and names of the newly created Box users.
        """

        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit create_user() function for each new user to executor
            for i in range(1, num_users+1):
                username = f"{prefix}{i}"
                executor.submit(self.create_user, username)

        self.logger.info(f'{num_users} users with prefix "{prefix}" created.')

        return list(self.sa_client.users(filter_term=prefix))

    def delete_user(self, user):
        """
        Deletes the Box user with the specified ID.

        Args:
        - user_id (str): The ID of the Box user to delete.

        Returns:
        - None
        """

        try:
            self.sa_client.user(user.id).delete(force=True)
            self.logger.info(f'User "{user.name}"(ID:{user.id}) deleted.')
        except BoxAPIException as e:
            self.error_logger.error(f'Error deleting user User "{user.name}"(ID:{user.id}). Error message: {e}')
            pass

    def delete_users_with_threads(self, prefix, num_threads=4):
        """
        Deletes all Box users with the specified name prefix, using multithreading to improve performance.

        Args:
        - prefix (str): The prefix used for the Box users to be deleted.
        - num_threads (int, optional): The number of threads to use for user deletion. Defaults to 4.

        Returns:
        - None
        """

        # Get all users with the specified prefix
        users_to_delete = []
        for user in self.sa_client.users(filter_term=prefix):
            users_to_delete.append(user)

        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit delete_user() function for each user to executor
            for user in users_to_delete:
                executor.submit(self.delete_user, user)

        self.logger.info(f'{len(users_to_delete)} users with prefix "{prefix}" deleted.')

    

    def create_group(self, group_name):
        """
        Creates a new Box group with the specified name.

        Args:
        - group_name (str): The name to use for the new Box group.

        Returns:
        - group_id (str): The ID of the newly created or existing Box group.
        """

        try:
            new_group = self.sa_client.create_group(group_name)
            self.logger.info(f'Group {group_name} created with ID {new_group.id}.')
            group =new_group
        except BoxAPIException as e:
            if e.status == 409:
                # If the group already exists, get the existing group's ID and return it
                existing_group = self.sa_client.get_groups(group_name)
                if existing_group:
                    group = list(existing_group)[0]
                    self.logger.warning(f'Group "{group.name}" already exists with ID {group.id}.')
                    return group
                else:
                    group = None
                    self.error_logger.error(f'Error retrieving existing group {group_name}. Error message: {e}')
            else:
                group = None
                self.error_logger.error(f'Error creating group {group_name}. Error message: {e}')
        return group


    def add_user_to_group(self, user, group, user_client):
        """
        Adds a Box user to a specified group.

        Args:
        - user (boxsdk.object.user.User): The Box user to add to the group.
        - group_id (str): The ID of the Box group to add the user to.

        Returns:
        - None
        """

        try:
            group_membership = user_client.group(group_id=group.id).add_member(user)
            self.logger.info(f'User "{user.name}"(ID:{user.id}) added to group "{group.name}"(ID:{group.id}).')
        except BoxAPIException as e:
            self.error_logger.error(f'Error adding user {user.name} to group. Error message: {e}')
            pass


    def add_users_to_group_with_threads(self, users, group, user_client, num_threads= 4):
        """
        Adds multiple Box users to a specified group using multithreading.

        Args:
        - users (List[boxsdk.object.user.User]): A list of Box users to add to the group.
        - group_id (str): The ID of the Box group to add the users to.
        - num_threads (int, optional): The number of threads to use for adding users to the group. Defaults to 4.

        Returns:
        - None
        """
        users_added = 0
        # Initialize ThreadPoolExecutor with specified number of threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:

            # Submit add_user_to_group() function for each user to executor
            for user in users:
                executor.submit(self.add_user_to_group, user, group, user_client)
                users_added+=1

        self.logger.info(f'{users_added} users added to group "{group.name}"(ID:{group.id})".')

    def add_group_collaboration(self, folder_id, group, role: str, user_client):
        """
        Adds a collaboration between the specified Box folder and group.

        Args:
        - folder_id (str): The ID of the Box folder to collaborate.
        - group_id (str): The ID of the Box group to collaborate.
        - role (str): The role of the collaborator. Must be one of 'viewer', 'editor', 'previewer', or 'uploader'.
        - user_client (boxsdk.Client): A Box API client instance authenticated as a user with access to the specified folder.

        Returns:
        - collaboration (boxsdk.object.collaboration.Collaboration): A Box collaboration object representing the newly created collaboration.

        Raises:
        - ValueError: If the specified role is not one of 'viewer', 'editor', 'previewer', or 'uploader'.
        """
        
        # Map role string to CollaborationRole attribute
        role_mapping = {
            'viewer': CollaborationRole.VIEWER,
            'editor': CollaborationRole.EDITOR,
            'previewer': CollaborationRole.PREVIEWER,
            'uploader': CollaborationRole.UPLOADER,
            'co-owner':CollaborationRole.CO_OWNER
        }
        if role not in role_mapping:
            raise ValueError(f"Invalid role '{role}'. Must be one of 'viewer', 'editor', 'previewer', or 'uploader'.")

        try:
            # Create the collaboration
            collaboration = user_client.folder(folder_id).collaborate(group, role_mapping[role])

            # Log the collaboration details
            collaborator = collaboration.accessible_by
            item = collaboration.item
            has_accepted = 'has' if collaboration.status == 'accepted' else 'has not'
            self.logger.info(f'"{collaborator.name}"(ID:{collaborator.id}) {has_accepted} accepted the collaboration to folder "{item.name}(ID:{item.id})"')
            
            return collaboration
        except BoxAPIException as e:
            if e.status == 409:
                self.logger.warning(f'Group "{group.name}"(ID:{group.id}) is already a collaborator for folder(ID: {folder_id})')
            else:
                self.logger.error(f'Error adding group(ID: {group.id}) as a collaborator for folder(ID: {folder_id}) with role {role}. Error message: {e}')
            return None
    
    ##### THIS NEEDS TO BE CLEANED UP
    def promote_closest_version(self, file_id, ransomware_start_date):
        """
        Promotes the closest previous version of the specified Box file based on the provided ransomware start date.

        Args:
        - file_id (str): The ID of the Box file to promote the closest previous version for.
        - ransomware_start_date (str): The start time (in ISO format) for the ransomware attack.

        Returns:
        - None
        """
        if not self.sa_client:
            self.logger.error('Box API client not initialized. promote_closest_version() stopped')
            return

      
        # Get closest previous version of the file
        closest_version_id = None
        lowest_found_time_diff = float('inf')
        with open('result.json') as json_file:
            compromised_files = json.load(json_file)
            file_details = compromised_files.get(file_id, {})
            previous_versions = file_details.get('previous_versions', [])
            for version in previous_versions:
                date_version_timestamp = get_date_object(version['created_at'])
                version_diff_from_attack = (ransomware_start_date - date_version_timestamp).total_seconds()
                if version_diff_from_attack < lowest_found_time_diff:
                    lowest_found_time_diff = version_diff_from_attack
                    closest_version_id = version['version_id']

            # Promote closest previous version
            if closest_version_id:
                version_to_promote = self.sa_client.file_version(closest_version_id)
                new_version = user_client.file(file_id).promote_version(version_to_promote)
                self.logger.info(f'File: {file_details.get("item_name")} | Closest Version: {closest_version_id} | Time Difference: {lowest_found_time_diff}s | Version {closest_version_id} promoted; new version {new_version.id} created')
            else:
                self.logger.warning(f'No previous versions found for file ID {file_id}')
                return
