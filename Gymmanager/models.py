from Gymmanager import db, app


class category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()