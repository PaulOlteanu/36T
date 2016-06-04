from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    path = db.Column(db.String(128))
    votes = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, title, path, votes=0):
        self.title = title
        self.path = path
        self.votes = votes

    def __repr__(self):
        return '<Photo %r>' % self.title
