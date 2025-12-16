import json
import hashlib
from models import User
from gym import app

def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

if __name__ == "__main__":
    with app.app_context():
        print(auth_user("letan", "123"))