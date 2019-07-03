from collections import namedtuple, OrderedDict
import datetime as dt
import csv
import os
import arrow
import json

Period = namedtuple("Period", ["name", "start_time", "end_time"])
datetime_format = "YYYY-MM-DD H:mm"


class BellSchedule:
    def __init__(
        self, name: str, tz: dt.tzinfo = None, schedule_date: dt.date = dt.date.today()
    ):
        self.periods = OrderedDict()
        self.tz = tz
        self.schedule_date = schedule_date
        self.name = name

    def add_period(
        self,
        period_name: str = None,
        start_time: dt.datetime = None,
        end_time: dt.datetime = None,
        period: Period = None,
    ) -> None:
        if period:
            self.periods[period.name] = period
        else:
            self.periods[period_name] = Period(
                period_name,
                arrow.Arrow.fromdatetime(start_time, tzinfo=self.tz),
                arrow.Arrow.fromdatetime(end_time, tzinfo=self.tz),
            )

    def remove_period(self, period_name: str = None, period_tup: Period = None) -> None:
        if period_tup:
            self.periods.pop(period_tup.name, None)
        else:
            self.periods.pop(period_name, None)

    def get_period(self, period_name: str) -> Period:
        return self.periods[period_name]

    def as_list(self, serializable=False) -> list:
        if serializable:
            return [
                {
                    "name": period.name,
                    "start_time": str(period.start_time),
                    "end_time": str(period.end_time),
                }
                for period in self.periods.values()
            ]
        else:
            return [period._asdict() for period in self.periods.values()]

    @classmethod
    def from_csv(cls, filename: str, schedule_date: dt.date, tz: dt.tzinfo = None):
        base = os.path.basename(filename)
        name = os.path.splitext(base)[0]
        bell_schedule = BellSchedule(name=name, tz=tz)
        bell_schedule.schedule_date = schedule_date
        with open(filename) as infile:
            bellreader = csv.DictReader(infile)
            for row in bellreader:
                start_time = arrow.get(
                    f"{schedule_date.strftime('%Y-%m-%d')} {row['start_time']}",
                    datetime_format,
                )
                end_time = arrow.get(
                    f"{schedule_date.strftime('%Y-%m-%d')} {row['end_time']}",
                    datetime_format,
                )
                bell_schedule.add_period(row["name"], start_time, end_time)

        return bell_schedule

    def to_csv(self, filename: str) -> None:
        with open(filename, "w") as outfile:
            fieldnames = ["name", "start_time", "end_time"]
            bellwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
            bellwriter.writeheader()
            for row in self.as_list():
                bellwriter.writerow(row)

    def current_period(self, current_time=dt.datetime.now()):
        current_time = arrow.Arrow.fromdatetime(current_time, tzinfo=self.tz)
        for period in self.periods.values():
            if period.start_time <= current_time and current_time < period.end_time:
                return period
        return None

    def as_dict(self):
        schedule_dict = {
            "name": self.name,
            "schedule_date": str(self.schedule_date),
            "tz": self.tz,
            "periods": self.as_list(serializable=True),
        }
        return schedule_dict

    def to_json(self):
        return json.dumps(self.as_dict(), indent=2)

    @classmethod
    def from_json(cls, filename: str):
        with open(filename, "r") as infile:
            sched_json = json.load(infile)
        new_bs = BellSchedule(
            sched_json["name"],
            tz=sched_json["tz"],
            schedule_date=sched_json["schedule_date"],
        )
        for period in sched_json['periods']:
            new_bs.add_period(period=Period(period.get('name'), period.get('start_time'), period.get('end_time')))
        return new_bs

