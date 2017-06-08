import os
import stock_check
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=os.environ['CHECK_INTERVAL'])
def timed_job():
    stock_check.run()

sched.start()
