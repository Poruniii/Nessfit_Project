from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
# this table mangae the many-to-many relatioship between Log and Exercise models.
log_exercise = db.Table('log_exercise', db.Column('log_id',db.Integer, db.ForeignKey('logs.id'),primary_key=True), db.Column('exercise_id', db.Integer, db.ForeignKey('exercises.id'),primary_key=True))

class Log(db.Model): 
    __tablename__='logs'
    id = db.Column(db.Integer,primary_key=True) 
    date = db.Column(db.Date, nullable=False) 
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    exercises = db.relationship('Exercise', secondary=log_exercise, backref='logs')
    __table_args__ = (UniqueConstraint('date','user_id',name='unique_date_user_id'),)

class Exercise(db.Model):
    __tablename__='exercises'
    id = db.Column(db.Integer,primary_key=True) 
    name = db.Column(db.String(50),unique=True,nullable=False)
    reps = db.Column(db.Integer,nullable=False)
    sets = db.Column(db.Integer,nullable=False)
    rest = db.Column(db.Integer,nullable=False)
    log_id = db.Column(db.Integer, db.ForeignKey('logs.id'))
    
class User(db.Model, UserMixin): 
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.String(20),nullable=False, unique = True)
    password = db.Column(db.String(20),nullable=False)
    logs = db.relationship('Log',backref='user',lazy='dynamic')

        