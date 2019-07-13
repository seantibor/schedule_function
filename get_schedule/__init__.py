import logging
import bell_schedule as bell
import datetime as dt
import json
from schedule_helper_functions import get_schedules, get_schedule
from dateutil import tz
from azure.storage.blob import BlockBlobService, PublicAccess
import os
import pytz

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python Get Schedule function processed a request.')
    
    schedule_date = req.route_params.get('date') or req.params.get('date')

    if schedule_date:
        try:
            schedule_date = dt.datetime.strptime(schedule_date, '%Y-%m-%d')
        except ValueError:
            return func.HttpResponse('Could not parse date string. Dates must be in YYYY-MM-DD format', status_code=400)
    else:
        schedule_date = dt.datetime.today()

    sched = get_schedule(schedule_date)

    if sched:
        func.HttpResponse.mimetype = 'application/json'
        return func.HttpResponse(sched.to_json())
    else:
        return func.HttpResponse(
             "Could not get bell schedule from storage",
             status_code=400
        )
