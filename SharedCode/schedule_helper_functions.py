import logging
import datetime as dt
import azure.functions as func
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
from dateutil import tz
from __app__.SharedCode.bell_schedule import BellSchedule # pylint: disable=import-error
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib
import urllib.parse as parse
import os
import icalendar
import pytz

connection_params = parse.parse_qs(os.environ['CosmosDBConnectionString'])

DEFAULT_TZNAME = "America/New_York"
names = {
        "ftl": "Fort Lauderdale",
        "boca": "Boca Raton",
        "middleschool": "Middle School",
        "upperschool": "Upper School",
        "default_schedule": "Regular Schedule",
    }

HOST = connection_params['AccountEndpoint'][0]
MASTER_KEY = connection_params['AccountKey'][0]
DATABASE_ID = "pcschedule"
COLLECTION_ID = "ftl-middleschool-schedules"

database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID

client = cosmos_client.CosmosClient(url_connection=HOST, auth={'masterKey': MASTER_KEY})

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

def get_default_schedule(campus: str, division: str, schedule_date: dt.datetime, tzname=DEFAULT_TZNAME) -> BellSchedule:
    DEFAULT_SCHEDULE_PATH = pathlib.Path(__file__).parent.parent / "SharedCode" / "default_schedules" / f"{campus}_{division}.csv"

    schedule = BellSchedule.from_csv(
    filename=DEFAULT_SCHEDULE_PATH,
    schedule_date=schedule_date,
    tzname=tzname,
    division=division,
    campus=campus,
    )
    schedule.name = "Regular Schedule"

    return schedule

def get_schedule_by_date(campus: str, division: str, date: dt.datetime, provide_default=True):
    result = get_latest_document(campus, division, date)
    if result:
        return BellSchedule.from_json(result)
    elif provide_default:
        return get_default_schedule(campus, division, schedule_date=date)
    else:
        return None

def get_latest_document(campus: str, division: str, date: dt.datetime):
    query = f"SELECT TOP 1 * from c where c.schedule_date = \"{date.strftime('%Y-%m-%d')}\" and c.campus = \"{campus}\" and c.division = \"{division}\" and c.ts <= GETCURRENTTIMESTAMP() order by c.ts DESC"
    results = get_schedule_documents(query)
    if results:
        return results[0]

def get_schedule_documents(query):
    documentlist = client.QueryItems(collection_link, query, options={ "enableCrossPartitionQuery": True })
    return list(documentlist)

def update_schedule_document(document):
    client.UpsertItem(collection_link, document)

def get_schedules(campus: str, division: str, start_date: dt.datetime, end_date: dt.datetime=None, num_days:int=1):
    if end_date is None:
        end_date = start_date + dt.timedelta(days=num_days)
    query = f"SELECT * from c where c.schedule_date >= \"{start_date.strftime('%Y-%m-%d')}\" AND \
            c.schedule_date <= \"{end_date.strftime('%Y-%m-%d')}\" AND c.campus = \"{campus}\" AND \
            c.division = \"{division}\" AND c.ts <= GETCURRENTTIMESTAMP() ORDER BY c.ts DESC" 
    return {schedule['schedule_date']: schedule for schedule in get_schedule_documents(query)}

def period_as_event(period, timezone) -> icalendar.Event:
    event = icalendar.Event()
    event.add('summary', period.name)
    event.add('dtstart', period.start_time.astimezone(timezone))
    event.add('dtend', period.end_time.astimezone(timezone))
    event.add('dtstamp', dt.datetime.now(tz=tz.UTC))
    event['uid'] = f'{period.name}/{period.start_time.isoformat()}/{period.end_time.isoformat()}'
    return event

def schedule_as_events(schedule: BellSchedule) -> list:
    event = icalendar.Event()
    timezone = tz.UTC
    event.add('summary', schedule.name)
    event.add('dtstart', schedule.schedule_date.date())
    event.add('dtend', schedule.schedule_date.date())
    event.add('dtstamp', dt.datetime.now(tz=tz.UTC))
    event['uid'] = f"{schedule.campus}/{schedule.division}/{schedule.name}/{schedule.schedule_date.isoformat()}"
    events = [period_as_event(period, timezone) for period in schedule.periods.values()]
    events.append(event)
    return events