import json

from gym import db, app
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum, Double, Text
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
    receipts=relationship("Receipt", backref="staff", lazy=True)
    def get_id(self):
        return (self.user_id)
    def __str__(self):
        return self.full_name

class Member(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    receipts = relationship("Receipt", backref="member", lazy=True)
    def get_id(self):
        return (self.user_id)
    def __str__(self):
        return self.full_name

class GoiTap(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(Double, nullable=False)
    description = Column(Text)
    receipts = relationship("Receipt", backref="package", lazy=True)

class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_amount = db.Column(Double, nullable=False)
    member_id=Column(Integer, ForeignKey(Member.user_id), nullable=False)
    package_id=Column(Integer, ForeignKey(GoiTap.id), nullable=False)
    staff_id=Column(Integer, ForeignKey(Staff.user_id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    is_paid=Column(Boolean, default=False)


class TrainingPlan(db.Model):
    __tablename__ = 'training_plan'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, ForeignKey('member.user_id'), nullable=False)  # Link với bảng Member
    member = db.relationship('Member', backref='training_plans', lazy=True)

    training_date = db.Column(db.Date, nullable=False)
    training_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.String(255))

    status = db.Column(db.String(20), default='pending')

    # Quan hệ để lấy danh sách bài tập con
    details = db.relationship('TrainingPlanDetail', backref='plan', lazy=True)

class TrainingPlanDetail(db.Model):
    __tablename__ = 'training_plan_detail'
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, ForeignKey('training_plan.id'), nullable=False)
    exercise_id = db.Column(db.Integer, ForeignKey('exercise.id'), nullable=False)
    # Tạo quan hệ để sau này truy xuất tên bài tập dễ dàng: detail.exercise.name
    exercise = db.relationship('Exercise')

    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    rest_time = db.Column(db.Integer)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    muscle_group = db.Column(db.String(50))
    video_link = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Exercise {self.name}>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import hashlib

        password = hashlib.md5("123".encode("utf-8")).hexdigest()
        u1 = Staff(username="letan", password=password, full_name="Nguyen Van A", email="nva@gmail.com", phone="12345", role=UserRole.LETAN)
        u2 = Staff(username="test", password=password, full_name="Nguyen Van B", email="nvb@gmail.com", phone="24680", role=UserRole.ADMIN)
        u3 = Staff(username="test2", password=password, full_name="Nguoi Dung", email="nd@gmail.com", phone="01273", role=UserRole.PT)
        u4 = Member(full_name="Hoi Vien", email="hv@gmail.com", phone="0849")
        p1=GoiTap(name="Gói 1 tháng", duration=1, price=299000)
        db.session.add_all([u1, u2, u3, u4, p1])
        db.session.commit()
        r1 = Receipt(total_amount=299000, member_id=u4.user_id, package_id=p1.id, staff_id=u2.user_id)

        db.session.add(r1)
        db.session.commit()