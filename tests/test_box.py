import pytest
from boxsdk import Client
from boxsdk.exception import BoxAPIException
from models.box import BoxAPI
from dotenv import load_dotenv
import os

load_dotenv()
config_path = os.getenv("config_file_path")  # Path to the Box API config file
admin_id = os.getenv("admin_id")
EVENT_TYPES_TO_QUERY = [
    "UPLOAD",
    "EDIT",
    "DELETE",
    "UNDELETE",
]  # Box event types to query
USER_TO_QUERY = os.getenv("user_to_query")  # User email to filter events
START_TIME_WINDOW = os.getenv("start_window")  # Start time window to query events
END_TIME_WINDOW = os.getenv("end_window")  # End time window to query events


@pytest.fixture(scope="module")
def box_api():
    config_path = "config.json"  # replace with valid path to your config file
    admin_id = "admin_id"  # replace with valid admin id
    return BoxAPI(config_path, admin_id)


def test_authenticate(box_api):
    assert isinstance(box_api.sa_client, Client)


def test_load_config(box_api):
    file_path = "config.json"  # replace with valid path to your config file
    assert isinstance(box_api.load_config(file_path), dict)


def test_get_admin_events(box_api):
    start_time = START_TIME_WINDOW
    end_time = END_TIME_WINDOW
    event_types = EVENT_TYPES_TO_QUERY
    events = box_api.get_admin_events(start_time, end_time, event_types)
    assert isinstance(events, list)


def test_get_file_versions(box_api):
    api = BoxAPI("config.json", "admin_id")
    file_id = "1135701622281"  # replace with valid file id
    admin_user = box_api.sa_client.user(user_id=admin_id)
    user_client = box_api.sa_client.as_user(admin_user)  # use sa_client for testing
    versions = box_api.get_file_versions(file_id, user_client)
    assert isinstance(versions, list)


def test_batch_get_file_versions(box_api):
    files = [
        (
            "1135697239535",
            {
                "file_id": "1135697239535",
                "event_created_by_user_id": "23539671305",
                "event_created_by_login": "rduchin@boxdemo.com",
                "item_type": "file",
                "item_name": "4generate-10.txt",
                "events": [
                    {"event_type": "EDIT", "event_time": "2023-02-08T22:46:31-08:00"},
                    {"event_type": "DELETE", "event_time": "2023-02-08T22:50:03-08:00"},
                    {
                        "event_type": "UNDELETE",
                        "event_time": "2023-02-08T23:11:07-08:00",
                    },
                ],
                "previous_versions": [],
            },
        ),
        (
            "1135699884430",
            {
                "file_id": "1135699884430",
                "event_created_by_user_id": "23539671305",
                "event_created_by_login": "rduchin@boxdemo.com",
                "item_type": "file",
                "item_name": "4generate-10.txt",
                "events": [
                    {"event_type": "EDIT", "event_time": "2023-02-08T22:46:31-08:00"},
                    {"event_type": "DELETE", "event_time": "2023-02-08T22:50:03-08:00"},
                    {
                        "event_type": "UNDELETE",
                        "event_time": "2023-02-08T23:11:07-08:00",
                    },
                ],
                "previous_versions": [],
            },
        ),
    ]

    admin_user = box_api.sa_client.user(user_id=admin_id)
    user_client = box_api.sa_client.as_user(admin_user)  # use sa_client for testing
    file_versions = box_api.batch_get_file_versions(files, user_client)
    assert isinstance(file_versions, list)

def test_create_user(box_api):
    username = "test_user"
    box_api.create_user(username)
    users = box_api.sa_client.users(filter_term=username)
    assert len(users) == 1
    assert users[0].name == username

def test_create_users_with_threads(box_api):
    prefix = "test_user_"
    num_users = 10
    users = box_api.create_users_with_threads(prefix, num_users, num_threads=4)
    assert len(users) == num_users
    for user in users:
        assert user.name.startswith(prefix)

def test_delete_user(box_api):
    # Create test user to delete
    username = "test_user_to_delete"
    box_api.create_user(username)
    user_to_delete = box_api.sa_client.users(filter_term=username)[0]
    user_id = user_to_delete.id

    # Delete user
    box_api.delete_user(user_id)

    # Check if user was deleted
    users = box_api.sa_client.users(filter_term=username)
    assert len(users) == 0

def test_delete_users_with_threads(box_api):
    # Create test users to delete
    prefix = "test_user_to_delete_"
    num_users = 10
    users = box_api.create_users_with_threads(prefix, num_users, num_threads=4)

    # Delete test users
    box_api.delete_users_with_threads(prefix, num_threads=4)

    # Check if users were deleted
    users = box_api.sa_client.users(filter_term=prefix)
    assert len(users) == 0

def test_create_group(box_api):
    group_name = "test_group"
    group = box_api.create_group(group_name)
    assert group is not None
    assert group.name == group_name

def test_add_user_to_group(box_api):
    # Create test user and group
    username = "test_user_to_add_to_group"
    box_api.create_user(username)
    user_to_add = box_api.sa_client.users(filter_term=username)[0]
    group_name = "test_group"
    group = box_api.create_group(group_name)

    # Add user to group
    admin_user = box_api.sa_client.user(user_id=box_api.admin_id)
    user_client = box_api.sa_client.as_user(admin_user)
    box_api.add_user_to_group(user_to_add, group.id, user_client)

    # Check if user was added to group
    members = group.get_memberships()
    assert len(members) == 1
    assert members[0].user.id == user_to_add.id

def test_add_users_to_group_with_threads(box_api):
    # Create test users and group
    prefix = "test_user_to_add_to_group_"
    num_users = 10
    users = box_api.create_users_with_threads(prefix, num_users, num_threads=4)
    group_name = "test_group"
    group = box_api.create_group(group_name)

    # Add users to group
    admin_user = box_api.sa_client.user(user_id=box_api.admin_id)
    user_client = box_api.sa_client.as_user(admin_user)
    box_api.add_users_to_group_with_threads(users, group.id, user_client, num_threads=4)

    # Check if users were added to group
    members = group.get_memberships()
    assert len(members) == num_users
    for member in members:
        assert member.user.id in [user.id for user in users]

# def test_restore_file(box_api):
#     file_id = "1135697239535" # replace with valid file id
#     admin_user = box_api.sa_client.user(user_id=admin_id)
#     user_client = box_api.sa_client.as_user(admin_user)  # use sa_client for testing
#     restored_file = box_api.restore_file(file_id, user_client)
#     assert restored_file is not None
