from apscheduler.schedulers.blocking import BlockingScheduler
import stock_check

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    stock_check.run()

sched.start()
