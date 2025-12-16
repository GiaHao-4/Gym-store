import json

from gym import db, app
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as RoleEnum
from flask_login import UserMixin

class UserRole(RoleEnum):
    ADMIN=1
    LETAN=2
    PT=3
    THUNGAN=4

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    def get_id(self):
        return (self.user_id)
    def __str__(self):
        return self.full_name

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import hashlib

        password = hashlib.md5("123".encode("utf-8")).hexdigest()
        u1 = User(username="letan", password=password, full_name="Nguyen Van A", email="nva@gmail.com", phone="12345")
        db.session.add(u1)
        db.session.commit()