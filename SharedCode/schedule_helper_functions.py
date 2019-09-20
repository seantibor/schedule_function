import logging
import datetime as dt
import azure.functions as func
from dateutil import tz
from __app__.SharedCode.bell_schedule import BellSchedule # pylint: disable=import-error
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

def is_weekend(date_in: dt.datetime) -> bool:
    return date_in.date().isoweekday() > 5

def render_html_schedule(schedule: BellSchedule, variables: dict, search_path: pathlib.Path=None) -> str:
    
    if search_path is None:
        search_path = pathlib.Path(__file__).parent / 'templates'
    env = Environment(
        loader=FileSystemLoader(search_path.as_posix(), followlinks=True),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("schedule.html")
    return template.render(schedule=schedule, **variables)
