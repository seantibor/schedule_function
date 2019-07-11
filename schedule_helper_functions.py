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

def get_schedule(schedules, sched_date):
    """
    returns a single schedule from the schedule dict
    """
    filename = 'default_schedule.csv'
    default_sched = bell.BellSchedule.from_csv(filename=filename, schedule_date=sched_date, timezone=DEFAULT_TIMEZONE)

    return schedules.get(dt.datetime.strftime(sched_date, '%Y-%m-%d'), default_sched)