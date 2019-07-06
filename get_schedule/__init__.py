import logging
import bell_schedule as bell
import datetime as dt
import json
from blob_storage import get_schedules

import azure.functions as func

filename = 'default_schedule.csv'

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
            schedule_date = dt.datetime.strptime(schedule_date, '%Y-%m-%d').date()
        except ValueError:
            return func.HttpResponse('Could not parse date string. Dates must be in YYYY-MM-DD format', status_code=400)
    else:
        schedule_date = dt.date.today()


    default_sched = bell.BellSchedule.from_csv(filename=filename, schedule_date=schedule_date, tz="US/Eastern")

    schedules = get_schedules(inputblob)

    sched = schedules.get(schedule_date.strftime('%Y-%m-%d'), default_sched)

    if sched:
        func.HttpResponse.mimetype = 'application/json'
        return func.HttpResponse(json.dumps(sched.as_dict()))
    else:
        return func.HttpResponse(
             "Could not get bell schedule from storage",
             status_code=400
        )
