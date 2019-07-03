import logging
import bell_schedule as bell
import datetime as dt
import json

import azure.functions as func

filename = 'default_schedule.csv'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    sched = bell.BellSchedule.from_csv(filename=filename, schedule_date=dt.date.today(), tz="US/Eastern")

    if sched:
        func.HttpResponse.mimetype = 'application/json'
        return func.HttpResponse(sched.to_json())
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
