import bell_schedule as bell
import logging
import datetime as dt
import json
import azure.functions as func

DEFAULT_SCHEDULE_PATH = 'default_schedule.csv'

def get_schedules(inputblob: func.InputStream) -> dict:
    try:
        schedules_json = json.loads(inputblob.read().decode('utf-8'))
        if schedules_json:
            schedules = {key: bell.BellSchedule.from_json(value) for key, value in schedules_json.items()}
    except ValueError:
        logging.info('Python add_schedules trigger function used default schedule')
        schedules = {"default": bell.BellSchedule.from_csv(DEFAULT_SCHEDULE_PATH, schedule_date=dt.date.today())}
    
    return schedules