import asyncio
import queue
import boxsdk, os
from boxsdk import JWTAuth
import tempfile, json
from dotenv import load_dotenv
# Set up Box.com SDK
def load_config(file_path):
    with open(file_path) as file:
        return json.load(file)

import time
load_dotenv()
config_path = os.getenv('config_file_path')
app_config =load_config(config_path)

# Setup authorization using config.json file
auth = JWTAuth.from_settings_dictionary(app_config)
auth.authenticate_instance()


# Create Box API client
client = boxsdk.Client(auth)

# Set up queue of work items
work_queue = queue.Queue()
for i in range(100):
    work_queue.put(i)

# Set up list of application users
user1 = client.create_user('App User 1', login=None)
user2 = client.create_user('App User 2', login=None)
user3 = client.create_user('App User 3', login=None)
users = [user1, user2, user3]

async def process_work():
    while not work_queue.empty():
        work_item = work_queue.get()
        assigned = False
        for user in users:
            try:
                with tempfile.NamedTemporaryFile(suffix='.txt') as f:
                    f.write(b'This is a dummy file')
                    f.seek(0)
                    await user.client.folder('folder_id').upload_async(f.name, f.name)
                assigned = True
                break
            except boxsdk.exception.BoxAPIException as e:
                if e.status == 429:
                    # Rate limit exceeded, try next user
                    continue
                else:
                    # Other error, raise exception
                    raise
        if not assigned:
            # All users rate limited, requeue item for later
            work_queue.put(work_item)
import datetime
async def test(num):
    t= datetime.datetime.now()
    print(f'sleep for {num} - {t}')
    await asyncio.sleep(num)
    return f'{num} was slept'
async def main():
    tasks = []
    for i in range(5):
        # Create 5 worker tasks to process work items
        print(i)
        task = asyncio.create_task(test(i))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    print(res)
    # # Delete all files created during test
    # root_folder = client.folder('folder_id')
    # for item in root_folder.get_items():
    #     item.delete()

# Run the main function
# asyncio.run(main())
asyncio.run(main())
