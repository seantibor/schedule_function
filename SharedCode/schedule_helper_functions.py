import logging
import datetime as dt
import azure.functions as func
from dateutil import tz

def is_weekend(date_in: dt.datetime) -> bool:
    return date_in.date().isoweekday() > 5