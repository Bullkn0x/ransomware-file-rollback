import json
import datetime as dt
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object

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
    """
    Flatten a nested JSON object by concatenating keys with a specified separator.

    Args:
        json_data (dict): A JSON object to be flattened.
        parent_key (str): The key of the parent object in the JSON data.
        sep (str): The separator string used to concatenate keys.

    Returns:
        dict: A flattened dictionary representation of the JSON data.
    """
    items = []
    for key, value in json_data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def merge_json(json1, json2):
    """
    Merge two JSON objects into a single dictionary.

    Args:
        json1 (dict): The first JSON object to merge.
        json2 (dict): The second JSON object to merge.

    Returns:
        dict: A dictionary representation of the merged JSON objects.
    """
    merged = json1.copy()
    merged.update(json2)
    return merged

def get_date_object(date_string):
    """ 
    Convert a date string in ISO 8601 format to a Python datetime object.

    Args:
        date_string (str): A date string in ISO 8601 format.

    Returns:
        datetime.datetime: A Python datetime object representing the date and time in the input string.
    """
    return iso8601.parse_date(date_string)

def get_date_string(date_object):
  """
    Convert a Python datetime object to a date string in RFC 3339 format (Box API Format).

    Args:
        date_object (datetime.datetime): A Python datetime object representing a date and time.

    Returns:
        str: A string representation of the date and time in the input datetime object, in RFC 3339 format.
    """

  return rfc3339.rfc3339(date_object)