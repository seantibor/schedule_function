import logging
from __app__.SharedCode import bell_schedule as bell
import datetime as dt
import json
from dateutil import tz
import os
import pytz
from __app__.SharedCode import schedule_helper_functions as shf
import pathlib

import azure.functions as func

DEFAULT_SCHEDULE_PATH = pathlib.Path(__file__).parent.parent / 'SharedCode' / 'default_schedule.csv'
DEFAULT_TIMEZONE = pytz.timezone('US/Eastern')


def main(req: func.HttpRequest, schedulesInput: func.DocumentList) -> func.HttpResponse:
    logging.info('Python Get Schedule function processed a request.')
    logging.info(DEFAULT_SCHEDULE_PATH)

    if 'date' in req.route_params:
        schedule_date = dt.datetime.strptime(req.route_params['date'], '%Y-%m-%d')
    else:
        schedule_date = dt.datetime.now()

    if shf.is_weekend(schedule_date):
        schedule = bell.BellSchedule.empty_schedule()
    elif schedulesInput:
        schedule = schedulesInput[0]
    else:
        schedule = bell.BellSchedule.from_csv(filename=DEFAULT_SCHEDULE_PATH, schedule_date=schedule_date, timezone=DEFAULT_TIMEZONE)

    return func.HttpResponse(
        body=schedule.to_json(),
        mimetype='application/json'
    )

