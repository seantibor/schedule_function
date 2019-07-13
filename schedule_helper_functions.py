import bell_schedule as bell
import logging
import datetime as dt
import json
import azure.functions as func
from azure.storage.blob import BlockBlobService
import pytz
import os

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


def get_schedule(schedule_date: dt.datetime) -> dict:
    """
    loads current schedule from the blob storage container
    """
    block_blob_service = BlockBlobService(connection_string=os.environ['ScheduleStorageConnectionString'])
    container_name = os.environ['ScheduleStorageContainerName']
    blobs = block_blob_service.list_blob_names(container_name)

    schedule_date_blob_name = f"schedule_{schedule_date.date().isoformat()}"
    if schedule_date_blob_name in blobs:
        schedule_blob = block_blob_service.get_blob_to_stream(container_name, schedule_date_blob_name)
        schedule_json = json.loads(schedule_blob.read().decode('utf-8'))
        sched = bell.BellSchedule.from_json(schedule_json)
    else:
        sched = bell.BellSchedule.from_csv(filename=DEFAULT_SCHEDULE_PATH, schedule_date=schedule_date, timezone=DEFAULT_TIMEZONE)

    return sched