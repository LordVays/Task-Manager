from extensions import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    completed = db.Column(db.Boolean, default = False)
    deadline = db.Column(db.DateTime, nullable = True)
    priority = db.Column(db.String(10), nullable = False, default='medium')
    category = db.Column(db.String(50), nullable = True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'