import logging
import bell_schedule as bell
import datetime as dt
import json
import requests
from blob_storage import get_schedules

import azure.functions as func

def main(req: func.HttpRequest, inputblob: func.InputStream,
         outputblob: func.Out[func.InputStream]) -> func.HttpResponse:
    logging.info('Python add_schedules trigger function processed new schedule')

    try:
        schedule = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Please pass a properly formatted schedule object in the request body",
             status_code=400
        )
    else:
        schedule = bell.BellSchedule.from_json(schedule)

    schedules = get_schedules(inputblob)

    schedules[schedule.schedule_date.strftime('%Y-%m-%d')] = schedule
    output_json = json.dumps({key: value.as_dict() for key, value in schedules.items()})
    
    outputblob.set(output_json)
        
    return func.HttpResponse(
        body=json.dumps(schedule.as_dict()),
        mimetype='application/json'
    )