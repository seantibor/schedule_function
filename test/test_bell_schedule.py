import sys
sys.path.insert(0, './SharedCode')
from SharedCode.bell_schedule import Period, BellSchedule
import datetime as dt
from dateutil import tz
import pytest
import os
from freezegun import freeze_time
import pytz

tzname = "US/Eastern"
timezone = tz.gettz(tzname)

test_date = dt.datetime(2019, 5, 15, 8, 25, tzinfo=timezone)

@pytest.fixture(scope="module")
def pc_bellschedule():
    return BellSchedule.from_csv(
        "test/test_input.csv", schedule_date=test_date, tzname=tzname
    )

def test_create_schedule():
    # Setup
    pass

def test_create_period():
    start_time = dt.datetime(2019, 5, 12, 8, 20, tzinfo=timezone)
    end_time = dt.datetime(2019, 5, 12, 9, 2, tzinfo=timezone)
    duration_min = (end_time - start_time).seconds / 60
    period = Period(name="1", start_time=start_time, end_time=end_time, duration_min=duration_min)
    assert period.name == "1"
    assert period.start_time == start_time
    assert period.end_time == end_time
    assert period.duration_min == duration_min

def test_add_period_by_attributes(pc_bellschedule):
    start_count = len(pc_bellschedule.periods)
    pc_bellschedule.add_period("X", test_date, test_date)
    assert len(pc_bellschedule.periods) == start_count + 1

def test_add_period_by_namedtuple(pc_bellschedule):
    start_count = len(pc_bellschedule.periods)
    test_period = Period("Y", test_date, test_date, 0)
    pc_bellschedule.add_period(period=test_period)
    assert len(pc_bellschedule.periods) == start_count + 1
    assert pc_bellschedule.get_period('Y') == test_period


def test_schedule_to_csv(pc_bellschedule):
    csv_file = "test/test_output.csv"
    pc_bellschedule.to_csv(csv_file)

def test_schedule_to_json(pc_bellschedule):
    output_json = pc_bellschedule.to_json()
    json_file = "test/test_output.json"
    with open(json_file, 'w') as outfile:
        outfile.write(output_json)
    assert '2019-05-15T08:21:00-04:00' in output_json
    assert 'schedule_date' in output_json

@freeze_time(test_date)
def test_csv_to_schedule():
    # Setup
    csv_file = "test/test_input.csv"
    pc_bellschedule = BellSchedule.from_csv(
        csv_file, schedule_date=test_date, tzname=tzname
    )
    assert isinstance(pc_bellschedule, BellSchedule)
    assert len(pc_bellschedule.periods) == 13

@freeze_time(test_date)
def test_json_to_schedule(pc_bellschedule):
    json_file = "test/test_input.json"
    pc_bellschedule = BellSchedule.read_json(json_file)
    assert isinstance(pc_bellschedule, BellSchedule)
    assert len(pc_bellschedule.periods) == 12

def test_current_period(pc_bellschedule):
    period = pc_bellschedule.current_period(test_date)
    assert period.name == "1"

def test_no_current_period(pc_bellschedule):
    test_time = dt.datetime(2019, 5, 14, 18, 25, tzinfo=timezone)
    period = pc_bellschedule.current_period(current_time=test_time)
    assert period is None


def test_remove_period_by_name(pc_bellschedule):
    start_count = len(pc_bellschedule.periods)
    pc_bellschedule.remove_period("X")
    assert len(pc_bellschedule.periods) == start_count - 1

@freeze_time(test_date)
def test_remove_period_by_namedtuple(pc_bellschedule):
    start_count = len(pc_bellschedule.periods)
    pc_bellschedule.remove_period(
        period_tup=Period("Y", dt.datetime.now(), dt.datetime.now(), 0)
    )
    assert len(pc_bellschedule.periods) == start_count - 1

def test_empty_schedule():
    empty_schedule = BellSchedule.empty_schedule()
    assert empty_schedule.name == 'No Classes'
    assert len(empty_schedule.periods) == 0
    assert empty_schedule.schedule_date.date() == dt.datetime.now(dt.timezone.utc).date()
