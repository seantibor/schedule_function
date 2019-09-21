import logging
import datetime as dt
from dateutil import tz
import pathlib
from urllib.parse import urljoin
from jinja2 import TemplateNotFound
from __app__.SharedCode import schedule_helper_functions as shf # pylint: disable=import-error
from __app__.SharedCode import bell_schedule as bell  # pylint: disable=import-error


import azure.functions as func

DEFAULT_SCHEDULE_PATH = (
    pathlib.Path(__file__).parent.parent / "SharedCode" / "default_schedule.csv"
)
DEFAULT_TZNAME = "America/New_York"
DEFAULT_TZINFO = tz.gettz(DEFAULT_TZNAME)
DEFAULT_DATE_FORMAT = "%Y-%m-%d"


async def main(
    req: func.HttpRequest, schedulesInput: func.DocumentList
) -> func.HttpResponse:


    schedule_date = req.route_params.get("date")
    logging.info(f"Python Get Schedule function processed a request for {schedule_date}.")
    campus = req.route_params.get("campus")
    division = req.route_params.get("division")
    names = {
        "ftl": "Fort Lauderdale",
        "boca": "Boca Raton",
        "middleschool": "Middle School",
        "upperschool": "Upper School",
        "default_schedule": "Regular Schedule",
    }

    if schedule_date is not None:
        schedule_date = dt.datetime.strptime(
            schedule_date, DEFAULT_DATE_FORMAT
        ).replace(tzinfo=tz.gettz(DEFAULT_TZNAME))
    else:
        schedule_date = dt.datetime.today().replace(tzinfo=tz.gettz(DEFAULT_TZNAME))
        redirect_url = urljoin(
            req.url + "/", schedule_date.strftime(DEFAULT_DATE_FORMAT)
        )
        print(f"Redirecting missing date code to {redirect_url}")
        return func.HttpResponse(status_code=301, headers={"Location": redirect_url})

    if schedulesInput:
        schedule = bell.BellSchedule.from_json(schedulesInput[0])
    elif shf.is_weekend(schedule_date):
        schedule = bell.BellSchedule.empty_schedule(schedule_date)
        schedule.name = 'No Classes - Weekend'
    else:
        schedule = bell.BellSchedule.from_csv(
            filename=DEFAULT_SCHEDULE_PATH,
            schedule_date=schedule_date,
            tzname=DEFAULT_TZNAME,
        )

    if req.headers.get("Accept") == "application/json":
        return func.HttpResponse(body=schedule.to_json(), mimetype="application/json")

    tomorrow_url = urljoin(
            req.url, (schedule_date + dt.timedelta(days=1)).strftime(DEFAULT_DATE_FORMAT)
        )
    yesterday_url = urljoin(
            req.url, (schedule_date - dt.timedelta(days=1)).strftime(DEFAULT_DATE_FORMAT)
        )
    bookmark_url = urljoin(req.url, f'/api/{campus}/{division}/schedule/')

    variables = {
        "campus": names[campus],
        "division": names[division],
        "schedule_name": names.get(schedule.name, schedule.name),
        "yesterday": yesterday_url,
        "tomorrow": tomorrow_url,
        "bookmark_url": bookmark_url,
        "today": schedule_date.date() == dt.datetime.today().date()
    }
    template_path = pathlib.Path(__file__).parent / "templates"

    try:
        html = shf.render_html_schedule(schedule, variables, search_path=template_path)
    except TemplateNotFound:
        print(f"Searched for templates in {template_path.as_posix()}")
    return func.HttpResponse(body=html, mimetype="text/html")

