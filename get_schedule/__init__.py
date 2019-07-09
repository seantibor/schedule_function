import logging
import bell_schedule as bell
import datetime as dt
import json
from blob_storage import get_schedules, get_schedule
from dateutil import tz

import azure.functions as func

def main(req: func.HttpRequest, inputblob: func.InputStream) -> func.HttpResponse:
    logging.info('Python Get Schedule function processed a request.')

    schedule_date = req.params.get('date')
    if not schedule_date:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            schedule_date = req_body.get('date')

    if schedule_date:
        try:
            schedule_date = dt.datetime.strptime(schedule_date, '%Y-%m-%d')
        except ValueError:
            return func.HttpResponse('Could not parse date string. Dates must be in YYYY-MM-DD format', status_code=400)
    else:
        schedule_date = dt.datetime.today()

    
    schedules = get_schedules(inputblob)

    sched = get_schedule(schedules, schedule_date)

    if sched:
        func.HttpResponse.mimetype = 'application/json'
        return func.HttpResponse(sched.to_json())
    else:
        return func.HttpResponse(
             "Could not get bell schedule from storage",
             status_code=400
        )
