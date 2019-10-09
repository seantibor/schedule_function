import logging
import datetime as dt
from dateutil import tz
from __app__.SharedCode import schedule_helper_functions as shf  # pylint: disable=import-error
from __app__.SharedCode import bell_schedule as bell  # pylint: disable=import-error
import ics

import azure.functions as func

DEFAULT_TZNAME = "America/New_York"
DEFAULT_TZINFO = tz.gettz(DEFAULT_TZNAME)
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_NUM_DAYS = 14


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(
        f"Python iCal Schedule function processed a request."
    )
    campus = req.route_params.get("campus")
    division = req.route_params.get("division")
    names = {
        "ftl": "Fort Lauderdale",
        "boca": "Boca Raton",
        "middleschool": "Middle School",
        "upperschool": "Upper School",
        "default_schedule": "Regular Schedule",
    }
    start_date = dt.datetime.now(tz=DEFAULT_TZINFO)
    schedules = shf.get_schedules(campus, division, start_date, num_days=DEFAULT_NUM_DAYS)
    schedules = {date: bell.BellSchedule.from_json(schedule) for date, schedule in schedules.items()}
    cal = ics.Calendar()
    for date in (start_date + dt.timedelta(days=i) for i in range(DEFAULT_NUM_DAYS)):
        schedule = schedules.get(date, shf.get_default_schedule(campus, division, date))
        cal.events.add(ics.Event(name=schedule.name, begin=schedule.schedule_date).make_all_day())
        for period in schedule.periods.values():
            cal.events.add(ics.Event(name=period.name, begin=period.start_time, end=period.end_time))

    return func.HttpResponse(body=str(cal), mimetype="text/calendar")