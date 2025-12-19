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

class Staff(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    role=db.Column(Enum(UserRole))
    def get_id(self):
        return (self.user_id)
    def __str__(self):
        return self.full_name

class Member(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    def get_id(self):
        return (self.user_id)
    def __str__(self):
        return self.full_name

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import hashlib

        password = hashlib.md5("123".encode("utf-8")).hexdigest()
        u1 = Staff(username="letan", password=password, full_name="Nguyen Van A", email="nva@gmail.com", phone="12345", role=UserRole.LETAN)
        u2 = Staff(username="test", password=password, full_name="Nguyen Van B", email="nvb@gmail.com", phone="24680", role=UserRole.ADMIN)
        u3 = Staff(username="test2", password=password, full_name="Nguoi Dung", email="nd@gmail.com", phone="01273", role=UserRole.PT)
        u4 = Member(full_name="Hoi Vien", email="hv@gmail.com", phone="0849")
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()