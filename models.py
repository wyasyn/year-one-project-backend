from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False, unique=True)
    answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<QA {self.question}>'

class UpcomingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # Event title
    description = db.Column(db.Text, nullable=False)  # Event details
    date = db.Column(db.Date, nullable=False)  # Event date

    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'


class ImportantCommunication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # Communication title
    message = db.Column(db.Text, nullable=False)  # Communication details
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))  # Use timezone-aware datetime

    def __repr__(self):
        return f'<Communication {self.title} posted on {self.date_posted}>'

