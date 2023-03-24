import datetime as dt
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object

def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)
indate='2023-02-09T01:45:05-08:00'

pydate =get_date_object(indate)

print(pydate)