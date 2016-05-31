from app import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    path = db.Column(db.String(128))

    def __init__(self, title, path):
        self.title = title
        self.path = path

    def __repr__(self):
        return '<Photo %r>' % self.title
