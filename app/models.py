from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    filename = db.Column(db.String(128), unique=True)
    mimetype = db.Column(db.String(128), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, title, filename, mimetype):
        self.title = title
        self.filename = filename
        self.mimetype = mimetype

    def __repr__(self):
        return "<Photo ID: {}, Title: {}, Votes: {}, Creation_Date: {}>".format(self.id, self.title, self.votes, self.created_on)
