import json
import hashlib
from models import Staff
from gym import app

def auth_user(username, password, role):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return Staff.query.filter(Staff.username.__eq__(username), Staff.password.__eq__(password),Staff.role.__eq__(role)).first()

def get_user_by_id(user_id):
    return Staff.query.get(user_id)

if __name__ == "__main__":
    with app.app_context():
        print(auth_user("letan", "123"))