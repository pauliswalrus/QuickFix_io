from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """ User Model """


    __tablename__ = "users_new"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(), nullable=False)
    status = db.Column(db.Integer(), default=1)

class History(db.Model):
    """ History Model """

    __tablename__="history"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)

class Message(db.Model):
    """ Message Model """

    __tablename__= "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    username = db.Column(db.String(25), nullable=False)
    room = db.Column(db.String(25), nullable=False)
