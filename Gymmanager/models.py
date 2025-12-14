from Gymmanager import db, app


class users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.Integer, nullable=False)

class members(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    dob = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    training_goal = db.Column(db.Integer, nullable=False)

class pts(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    certificate_id = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(500), nullable=False)
    years_experience = db.Column(db.Integer, nullable=False)

class workout_sessions(db.Model):
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.ForeignKey('members.user_id'), nullable=False)
    pt_id = db.Column(db.ForeignKey('pts.user_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500), nullable=False)

class exercises(db.Model):
    exercise_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    muscle_group = db.Column(db.Integer, nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=False)

class workout_details(db.Model):
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.ForeignKey('workout_sessions.session_id'), nullable=False)
    excise_id = db.Column(db.ForeignKey('exercises.exercise_id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.String(500), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()