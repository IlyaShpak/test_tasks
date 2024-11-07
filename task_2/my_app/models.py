from flask_login import UserMixin
from task_2.my_app import db, manager


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
