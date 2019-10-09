import logging
import datetime as dt
from dateutil import tz
from __app__.SharedCode import schedule_helper_functions as shf  # pylint: disable=import-error
from __app__.SharedCode import bell_schedule as bell  # pylint: disable=import-error
import icalendar

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

    start_date = dt.datetime.now(tz=DEFAULT_TZINFO)
    schedules = shf.get_schedules(campus, division, start_date, num_days=DEFAULT_NUM_DAYS)
    schedules = {date: bell.BellSchedule.from_json(schedule) for date, schedule in schedules.items()}
    cal = icalendar.Calendar()
    cal.add('prodid', f'PC Bell Schedule - https://pcbellschedule.azurewebsites.net/api/{campus}/{division}/schedule')
    cal.add('version', '2.0')
    cal.add('dtstamp', dt.datetime.now(tz=tz.UTC))
    for date in (start_date + dt.timedelta(days=i) for i in range(DEFAULT_NUM_DAYS)):
        if date.weekday() < 5:
            schedule = schedules.get(date, shf.get_default_schedule(campus, division, date))
            for event in shf.schedule_as_events(schedule):
                cal.add_component(event)
    return func.HttpResponse(body=cal.to_ical(), mimetype="text/calendar")