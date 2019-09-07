import logging
from __app__.SharedCode import bell_schedule as bell #pylint: disable=import-error
import datetime as dt
import json
from dateutil import tz, parser
import os
from __app__.SharedCode import schedule_helper_functions as shf #pylint: disable=import-error
import pathlib

import azure.functions as func

DEFAULT_SCHEDULE_PATH = pathlib.Path(__file__).parent.parent / 'SharedCode' / 'default_schedule.csv'
DEFAULT_TIMEZONE = tz.gettz('US/Eastern')


def main(req: func.HttpRequest, schedulesInput: func.DocumentList) -> func.HttpResponse:
    logging.info('Python Get Schedule function processed a request.')
    logging.info(DEFAULT_SCHEDULE_PATH)

    if 'date' in req.route_params:
        schedule_date = parser.parse(req.route_params['date'])
    else:
        schedule_date = dt.datetime.now(tz=DEFAULT_TIMEZONE)

    if schedulesInput:
        schedule = schedulesInput[0]
    elif shf.is_weekend(schedule_date):
        schedule = bell.BellSchedule.empty_schedule(schedule_date)
    else:
        schedule = bell.BellSchedule.from_csv(filename=DEFAULT_SCHEDULE_PATH, schedule_date=schedule_date, timezone=DEFAULT_TIMEZONE)

    return func.HttpResponse(
        body=schedule.to_json(),
        mimetype='application/json'
    )

