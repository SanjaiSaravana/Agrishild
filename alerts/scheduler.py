import schedule
import time
from datetime import datetime
from app import send_bulk_sms

last_sent_date = None   # prevents multiple sends in same day

def job():
    global last_sent_date
    today = datetime.now().date()

    if last_sent_date != today:
        print("Sending daily farmer advisory SMS...")
        send_bulk_sms()
        last_sent_date = today
    else:
        print("SMS already sent today")

# run every day at 07:00 AM
schedule.every().day.at("07:00").do(job)

print("Scheduler started... Waiting for 7:00 AM")

while True:
    schedule.run_pending()
    time.sleep(30)
