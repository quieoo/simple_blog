from datetime import datetime
from app import db

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text)  # Ensure this is long enough to store HTML content
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
