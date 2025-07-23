from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MedicineReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)  # Can use session or default for now
    medicine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    times = db.Column(db.String(200), nullable=False)  # "08:00,14:00,20:00"
