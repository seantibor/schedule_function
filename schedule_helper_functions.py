import bell_schedule as bell
import logging
import datetime as dt
import json
import azure.functions as func
import pytz

DEFAULT_SCHEDULE_PATH = 'default_schedule.csv'
DEFAULT_TIMEZONE = pytz.timezone('US/Eastern')

def get_schedules(inputblob: func.InputStream) -> dict:
    """
    load all current schedules from the blob storage container
    """
    try:
        schedules_json = json.loads(inputblob.read().decode('utf-8'))
        if schedules_json:
            schedules = {key: bell.BellSchedule.from_json(value) for key, value in schedules_json.items()}
    except ValueError:
        logging.info('Python add_schedules trigger function used default schedule')
        schedules = {"default": bell.BellSchedule.from_csv(DEFAULT_SCHEDULE_PATH, schedule_date=dt.datetime.today(),timezone=DEFAULT_TIMEZONE)}
    
    return schedules


def get_schedule(inputblob: func.InputStream) -> dict:
    """
    loads current schedule from the blob storage container
    """
    try:
        schedule_json = json.loads(inputblob.read().decode('utf-8'))
        schedule = bell.BellSchedule.from_json(schedule_json)
    except ValueError:
        # Return the default schedule if we can't find one in the blob container
        schedule = bell.BellSchedule.from_csv(DEFAULT_SCHEDULE_PATH, schedule_date=dt.datetime.today(),timezone=DEFAULT_TIMEZONE)
    
    return schedule