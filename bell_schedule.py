from collections import namedtuple, OrderedDict
import datetime as dt
import csv
import os
import arrow
import json
import pytz
from dateutil import parser

Period = namedtuple("Period", ["name", "start_time", "end_time"])
time_format = "%H:%M"
datetime_format = "%Y-%m-%dT%H:%M:%S%z"


class BellSchedule:
    """
    Represents a simple daily bell schedule for a school.

    Parameters:
    name: schedule name for human display
    timezone: a pytz object that will localize the dates and times 
        in the schedule. By default, all datetime objects are represented in UTC.
    schedule_date: the date of the schedule. defaults to today.
    """
    def __init__(
        self, name: str, timezone: dt.tzinfo = pytz.utc, schedule_date: dt.datetime = dt.datetime.utcnow()
    ):
        self.periods = OrderedDict()
        self.tz = timezone
        self.schedule_date = schedule_date.astimezone(pytz.utc)
        self.name = name

    def add_period(
        self,
        period_name: str = None,
        start_time: dt.datetime = None,
        end_time: dt.datetime = None,
        period: Period = None,
    ) -> None:
        if period is None:
            period = Period(
                period_name,
                start_time.astimezone(pytz.utc),
                end_time.astimezone(pytz.utc),
            )
            
        self.periods[period.name] = period
            

    def remove_period(self, period_name: str = None, period_tup: Period = None) -> None:
        if period_tup:
            self.periods.pop(period_tup.name, None)
        else:
            self.periods.pop(period_name, None)

    def get_period(self, period_name: str) -> Period:
        return self.periods[period_name]

    def periods_as_list(self, serializable=False) -> list:
        if serializable:
            return [
                {
                    "name": period.name,
                    "start_time": period.start_time.astimezone(self.tz).isoformat(),
                    "end_time": period.end_time.astimezone(self.tz).isoformat(),
                }
                for period in self.periods.values()
            ]
        else:
            return [period._asdict() for period in self.periods.values()]

    @classmethod
    def from_csv(cls, filename: str, schedule_date: dt.datetime, timezone: dt.tzinfo = pytz.utc):
        base = os.path.basename(filename)
        name = os.path.splitext(base)[0]
        schedule_date = schedule_date.astimezone(pytz.utc)
        bell_schedule = BellSchedule(name=name, schedule_date=schedule_date, timezone=timezone)
        with open(filename) as infile:
            bellreader = csv.DictReader(infile)
            for row in bellreader:
                start_time = dt.datetime.strptime(
                    f"{row['start_time']}",
                    time_format
                ).time()
                end_time = dt.datetime.strptime(f"{row['end_time']}",
                    time_format
                ).time()
                schedule_date_local = schedule_date.astimezone(timezone).date()
                start_time = timezone.localize(dt.datetime.combine(schedule_date_local, start_time)).astimezone(pytz.utc)
                end_time = timezone.localize(dt.datetime.combine(schedule_date_local, end_time)).astimezone(pytz.utc)
                bell_schedule.add_period(row["name"], start_time, end_time)

        return bell_schedule

    def to_csv(self, filename: str) -> None:
        with open(filename, "w") as outfile:
            fieldnames = ["name", "start_time", "end_time"]
            bellwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
            bellwriter.writeheader()
            for row in self.periods_as_list():
                bellwriter.writerow(row)

    def current_period(self, current_time=dt.datetime.now()):
        for period in self.periods.values():
            if period.start_time <= current_time and current_time < period.end_time:
                return period
        return None

    def as_dict(self):
        schedule_dict = {
            "name": self.name,
            "schedule_date": self.schedule_date.astimezone(self.tz).date().isoformat(),
            "utz_datetime": self.schedule_date.isoformat(),
            "timezone": str(self.tz),
            "periods": self.periods_as_list(serializable=True),
        }
        return schedule_dict

    def to_json(self, indent=False):
        return json.dumps(self.as_dict(), default=str)

    @classmethod
    def from_json(cls, sched_json: json):
        try:
            timezone = pytz.timezone(sched_json["timezone"])
        except pytz.exceptions.UnknownTimeZoneError:
            timezone = pytz.utc
        
        new_bs = BellSchedule(
            sched_json["name"],
            timezone=timezone,
            schedule_date=parser.parse(sched_json["schedule_date"])
        )
        for period in sched_json["periods"]:
            new_bs.add_period(
                period=Period(
                    period.get("name"), 
                    parser.parse(period.get("start_time")), 
                    parser.parse(period.get("end_time"))
                )
            )
        with open('last_schedule.json', 'w') as outfile:
            outfile.write(new_bs.schedule_date.isoformat())
        
        return new_bs

    @classmethod
    def read_json(cls, filename: str) -> json:
        with open(filename, "r") as infile:
            sched_json = json.load(infile)
        return BellSchedule.from_json(sched_json=sched_json)

    @classmethod
    def empty_schedule(cls, schedule_date=dt.datetime.utcnow()):
        return BellSchedule('No Classes', timezone=pytz.timezone("US/Eastern"), schedule_date=schedule_date)