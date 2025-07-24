from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app import db
from app.models import MedicineReminder  # Update import as per your structure
from app.utils import send_email_reminder  # Custom function we'll write

def check_and_send_reminders():
    now = datetime.now().strftime("%H:%M")
    current_date = datetime.now().date()

    reminders = MedicineReminder.query.filter_by(is_active=True).all()
    for reminder in reminders:
        if str(current_date) >= str(reminder.start_date) and str(current_date) <= str(reminder.end_date):
            if now in reminder.times:  # example: times = ['08:00', '14:00', '20:00']
                print(f"⏰ Sending reminder for {reminder.medicine_name}")
                # Trigger in-app or email reminder here
                send_email_reminder(reminder)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_send_reminders, trigger="interval", minutes=1)
    scheduler.start()
