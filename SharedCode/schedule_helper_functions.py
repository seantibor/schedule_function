import logging
import datetime as dt
import azure.functions as func
from dateutil import tz
from SharedCode.bell_schedule import BellSchedule
from jinja2 import Environment, FileSystemLoader, select_autoescape


def is_weekend(date_in: dt.datetime) -> bool:
    return date_in.date().isoweekday() > 5

def render_html_schedule(schedule: BellSchedule, variables: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(["./templates", "./get_schedule/templates"]),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("schedule.html")
    return template.render(schedule=schedule, **variables)
