import json
import datetime as dt
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
from cryptography.fernet import Fernet

def read_json_file(filepath):
    """
    Reads JSON data from a file and returns a Python dictionary.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data

def write_json_file(filepath, data):
    """
    Writes Python dictionary to a JSON file.
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def pretty_print_json(data):
    """
    Returns a pretty-printed JSON string from a Python dictionary.
    """
    return json.dumps(data, indent=4)

def create_json_file(filepath, data):
    """
    Creates a new JSON file and writes Python dictionary data to it.
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def flatten_json(json_data, parent_key='', sep='_'):
    items = []
    for key, value in json_data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def merge_json(json1, json2):
    merged = json1.copy()
    merged.update(json2)
    return merged

def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

def generate_key():
    key = Fernet.generate_key()
    with open(".env", "a") as f:
        f.write(f'\nSECRET_KEY="{key.decode("utf-8")}"')
    return key