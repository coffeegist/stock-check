from apscheduler.schedulers.blocking import BlockingScheduler
import stock_check

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30)
def timed_job():
    stock_check.run()

sched.start()
