from .extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user')  # 'admin' or 'user'

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    cpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)
    disk_usage = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='umknown')  # 'online', 'offline', 'unknown'
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)  # allow nulls, optional



class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

