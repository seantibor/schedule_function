"""
This library is used to represent the daily bell schedule for schools. 
For example, a school may have a default daily schedule for each class 
period, plus a number of special schedules for things like assemblies and events.

The class BellSchedule holds an ordered collection of Periods. A Period has a name, start, and end time.
All schedules are stored with timezone-aware datetime objects and can be serialized to and from JSON and CSV.
"""
from collections import namedtuple, OrderedDict
import datetime as dt
import csv
import json
from dateutil import tz
import pathlib
from typing import Union
import iso8601

Period = namedtuple("Period", ["name", "start_time", "end_time", "duration_min"])
time_format = "%H:%M"
datetime_format = "%Y-%m-%dT%H:%M:%S%z"
date_format = "%Y-%m-%d"
UTC_IANA_NAME = "Etc/UTC"


class BellSchedule:
    """
    Represents a simple daily bell schedule for a school.

    Parameters:
    name: schedule name for human display
    tzname: an IANA-standard string that will be used to localize the dates and times 
        in the schedule. If a tzname is not provided, the schedule will be stored in UTC.
    schedule_date: the date of the schedule. defaults to today.
    """

    def __init__(
        self,
        name: str,
        tzname: str = "Etc/UTC",
        schedule_date: dt.datetime = dt.datetime.now(tz=tz.UTC),
    ):
        # Datetime objects must be timezone-aware
        if schedule_date.tzinfo is None:
            raise ValueError("schedule_date must be timezone-aware")

        self.tz = tz.gettz(tzname)
        self.periods = OrderedDict()
        self.schedule_date = schedule_date
        self.tzname = tzname
        self.name = name
        self.ts = dt.datetime.utcnow().timestamp() #used for caching

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
                start_time,
                end_time,
                (end_time - start_time).seconds / 60,
            )

        self.periods[period.name] = period

    def remove_period(self, period: Union[Period, str]) -> None:
        if isinstance(period, Period):
            self.periods.pop(period.name, None)
        else:
            self.periods.pop(period, None)

    def get_period(self, period_name: str) -> Period:
        return self.periods[period_name]

    def periods_as_list(self, serializable=False) -> list:
        if serializable:
            return [
                {
                    "name": period.name,
                    "start_time": period.start_time.astimezone(self.tz).isoformat(),
                    "end_time": period.end_time.astimezone(self.tz).isoformat(),
                    "duration_min": period.duration_min,
                }
                for period in self.periods.values()
            ]
        else:
            return [period._asdict() for period in self.periods.values()]

    @classmethod
    def from_csv(
        cls,
        filename: Union[str, pathlib.Path],
        schedule_date: dt.datetime,
        tzname: str = "Etc/UTC",
    ):
        timezone = tz.gettz(tzname)
        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        name = filename.stem
        if schedule_date.tzinfo is None:
            raise ValueError("schedule_date missing timezone info")
        bell_schedule = BellSchedule(
            name=name, schedule_date=schedule_date, tzname=tzname
        )
        with filename.open() as infile:
            bellreader = csv.DictReader(infile)
            for row in bellreader:
                start_time = dt.datetime.strptime(
                    f"{row['start_time']}", time_format
                ).time()
                end_time = dt.datetime.strptime(
                    f"{row['end_time']}", time_format
                ).time()
                schedule_date_local = schedule_date.date()
                start_time = dt.datetime.combine(
                    schedule_date_local, start_time, tzinfo=timezone
                )
                end_time = dt.datetime.combine(
                    schedule_date_local, end_time, tzinfo=timezone
                )
                bell_schedule.add_period(row["name"], start_time, end_time)

        return bell_schedule

    def to_csv(self, filename: str) -> None:
        with open(filename, "w") as outfile:
            fieldnames = ["name", "start_time", "end_time", "duration_min"]
            bellwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
            bellwriter.writeheader()
            for row in self.periods_as_list():
                bellwriter.writerow(row)

    def current_period(self, current_time=dt.datetime.utcnow()):
        for period in self.periods.values():
            if period.start_time <= current_time and current_time < period.end_time:
                return period
        return None

    def as_dict(self):
        schedule_dict = {
            "name": self.name,
            "schedule_date": self.schedule_date.strftime(date_format),
            "ts": self.ts,
            "tzname": self.tzname,
            "periods": self.periods_as_list(serializable=True),
        }
        return schedule_dict

    def to_json(self, indent=False):
        return json.dumps(self.as_dict(), default=str)

    @classmethod
    def from_json(cls, sched_json: json):
        timezone = tz.gettz(sched_json['tzname'])
        schedule_date = dt.datetime.strptime(sched_json["schedule_date"], date_format)
        schedule_date = schedule_date.replace(tzinfo=timezone)

        new_bs = BellSchedule(
            sched_json["name"],
            tzname=sched_json["tzname"],
            schedule_date=schedule_date,
        )
        new_bs.ts = sched_json.get("ts", dt.datetime.utcnow().timestamp())
        for period in sched_json["periods"]:
            start_time = iso8601.parse_date(period.get("start_time"))
            end_time = iso8601.parse_date(period.get("end_time"))
            new_bs.add_period(
                period=Period(
                    period.get("name"),
                    start_time,
                    end_time,
                    (end_time - start_time).seconds / 60,
                )
            )

        return new_bs

    @classmethod
    def read_json(cls, filename: str) -> json:
        with open(filename, "r") as infile:
            sched_json = json.load(infile)
        return BellSchedule.from_json(sched_json=sched_json)

    @classmethod
    def empty_schedule(cls, schedule_date=dt.datetime.now(tz=tz.UTC)):
        return BellSchedule(
            "No Classes", tzname=UTC_IANA_NAME, schedule_date=schedule_date
        )

