import queue
import boxsdk, os
from boxsdk import JWTAuth
import tempfile, json
import threading
import datetime
from dotenv import load_dotenv

# Set up Box.com SDK
def load_config(file_path):
    """
    Load configuration settings from a JSON file.

    Args:
        file_path (str): Path to the JSON configuration file.

    Returns:
        dict: Configuration settings.
    """
    with open(file_path) as file:
        return json.load(file)

load_dotenv()
config_path = os.getenv('config_file_path')
app_config = load_config(config_path)

# Setup authorization using config.json file
auth = JWTAuth.from_settings_dictionary(app_config)
auth.authenticate_instance()

# Set up queue of work items
work_queue = queue.Queue()

# Define worker function for creating users
def create_users(work_queue):
    """
    Worker function for creating users.

    Args:
        work_queue (Queue): Queue of work items containing user prefixes.
    """
    client = boxsdk.Client(auth)
    while not work_queue.empty():
        user_prefix = work_queue.get()
        user_name = f'{user_prefix}{user_counter()}'
        new_user = client.create_user(user_name, login=None)
        print(f'New user created: {user_name}( ID:{new_user.id})')

# Define worker function for deleting users
def delete_users(work_queue):
    """
    Worker function for deleting users.

    Args:
        work_queue (Queue): Queue of work items containing users to delete.
    """
    client = boxsdk.Client(auth)
    while not work_queue.empty():
        user = work_queue.get()
        client.user(user.id).delete(force=False)
        t = datetime.datetime.now()
        print(f'{user.id} was deleted at {t}')

# Define function to generate user counter
def user_counter():
    """
    Function to generate a unique user counter for naming users.

    Returns:
        int: Current user counter value.
    """
    user_counter.count += 1
    return user_counter.count

user_counter.count = 0

# Define function to create threads for a given worker function and work queue
def create_threads(worker_fn, num_threads, work_queue):
    """
    Create a specified number of worker threads for a given worker function and work queue.

    Args:
        worker_fn (function): Function to execute as worker thread.
        num_threads (int): Number of threads to create.
        work_queue (Queue): Queue of work items to process.

    Returns:
        list: List of worker threads created.
    """
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_fn, args=(work_queue,))
        threads.append(thread)
        thread.start()
    return threads

# Define function for creating users with threads
def create_users_with_threads(user_prefix, num_users, num_threads):
    """
    Create a specified number of Box.com application users with threads.

    Args:
        user_prefix (str): Prefix for user names.
        num_users (int): Number of users to create.
        num_threads (int): Number of threads to use for user creation.

    Returns:
        list: List of Box.com application users created.
    """
    start_time = datetime.datetime.now()

    # Add user prefixes to work queue
    for i in range(num_users):
        work_queue.put(user_prefix)

    # Create worker threads for user creation
    create_threads(create_users, num_threads, work_queue)

    # Wait for all user creation threads to finish
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.join()

    end_time = datetime.datetime.now()
    print(f'All users created in {end_time - start_time}')

    client = boxsdk.Client(auth)
    return client.users(filter_term=user_prefix)

# Define function for deleting users with threads
def delete_users_with_threads(user_prefix, num_threads):
    """
    Delete all Box.com application users with a given prefix using multiple threads.

    Args:
        user_prefix (str): Prefix for user names.
        num_threads (int): Number of threads to use for user deletion.

    Returns:
        datetime.timedelta: Time taken to delete all users.
    """
    start_time = datetime.datetime.now()

    # Set up list of application users to delete
    client = boxsdk.Client(auth)
    app_users = client.users(filter_term=user_prefix)

    # Add users to work queue
    for user in app_users:
        work_queue.put(user)

    # Create worker threads for user deletion
    delete_threads = create_threads(delete_users, num_threads, work_queue)

    # Wait for all user deletion threads to finish
    for thread in delete_threads:
        thread.join()

    end_time = datetime.datetime.now()
    print(f'All users deleted in {end_time - start_time}')
    return end_time - start_time

# Call create_users_with_threads function to create users with threads
created_users  = create_users_with_threads('ransomwareAppUser', 50, 10)

# Call delete_users_with_threads function to delete users with threads
delete_time = delete_users_with_threads('ransomwareAppUser', 20)
print(f'Time taken to delete users with threads: {delete_time}')
