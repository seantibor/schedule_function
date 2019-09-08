import logging
import bell_schedule as bell #pylint: disable=import-error
import datetime as dt
import json
from dateutil import tz, parser
import os
from __app__.SharedCode import schedule_helper_functions as shf #pylint: disable=import-error
import pathlib

import azure.functions as func

DEFAULT_SCHEDULE_PATH = pathlib.Path(__file__).parent.parent / 'SharedCode' / 'default_schedule.csv'
DEFAULT_TZNAME = 'America/New_York'
DEFAULT_DATE_FORMAT = "%Y-%m-%d"



def main(req: func.HttpRequest, schedulesInput: func.DocumentList) -> func.HttpResponse:
    logging.info('Python Get Schedule function processed a request.')
    logging.info(DEFAULT_SCHEDULE_PATH)

    schedule_date = req.route_params.get('date')
    if schedule_date:
        schedule_date = dt.datetime.strptime(schedule_date, DEFAULT_DATE_FORMAT)
    else:
        schedule_date = dt.datetime.today()
    schedule_date = schedule_date.replace(tzinfo=tz.gettz(DEFAULT_TZNAME))

    if schedulesInput:
        schedule = schedulesInput[0]
    elif shf.is_weekend(schedule_date):
        schedule = bell.BellSchedule.empty_schedule(schedule_date)
    else:
        schedule = bell.BellSchedule.from_csv(filename=DEFAULT_SCHEDULE_PATH, schedule_date=schedule_date, tzname=DEFAULT_TZNAME)

    return func.HttpResponse(
        body=schedule.to_json(),
        mimetype='application/json'
    )

