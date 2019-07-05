from pymongo import MongoClient
import bell_schedule as bell
import datetime as dt

filename = 'default_schedule.csv'

sched = bell.BellSchedule.from_csv(filename, dt.date.today(), tz ='US/Eastern')

client = MongoClient()
db = client.pcbellschedules

sched.name = "Default Schedule"

result = db.schedules.insert(sched.to_json())
print(f"Added the {sched.name} schedule for {sched.schedule_date}")