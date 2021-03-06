import logging
from __app__.SharedCode import bell_schedule as bell #pylint: disable=import-error
from __app__.SharedCode import schedule_helper_functions as shf #pylint: disable=import-error
import datetime as dt
import json
import requests

import azure.functions as func

def main(req: func.HttpRequest, scheduleOutput: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python add_schedules trigger function processed new schedule')

    try:
        schedule = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Please pass a properly formatted schedule object in the request body",
             status_code=400)
    else:
        schedule = bell.BellSchedule.from_json(schedule)

    document = shf.get_latest_document(schedule.campus, schedule.division, schedule.schedule_date)
    if document:
        document.update(schedule.as_dict())
        shf.update_schedule_document(document)
    else:
        scheduleOutput.set(func.Document.from_json(schedule.to_json()))
        
    return func.HttpResponse(
        body=schedule.to_json(),
        mimetype='application/json'
    )