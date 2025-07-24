import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_reminder(reminder):
    sender_email = "youremail@gmail.com"
    sender_password = "yourpassword"
    receiver_email = reminder.user.email  # assuming relation exists

    subject = f"💊 Reminder: {reminder.medicine_name}"
    body = f"Time to take your medicine: {reminder.dosage} of {reminder.medicine_name}."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
