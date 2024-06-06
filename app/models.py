from datetime import datetime
from app import db

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    keywords = db.Column(db.String(200))  # New field for storing keywords

    def __repr__(self):
        return f'<BlogPost {self.title}>'
