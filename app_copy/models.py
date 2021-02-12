from datetime import datetime

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    occupation=db.Column(db.String(120))
    home_address=db.Column(db.String(200))
    office_address = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(200))
    registered = db.Column(db.DateTime(), default=datetime.utcnow())
    user_id = db.Column(db.Integer)
    

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    poster = db.Column(db.String(200))
    content = db.Column(db.Text)
    created = db.Column(db.DateTime(), default=datetime.utcnow())
    user_id = db.Column(db.Integer)

