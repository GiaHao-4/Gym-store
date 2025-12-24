from gym import db, app
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as RoleEnum
from flask_login import UserMixin
import hashlib


# --- 1. ĐỊNH NGHĨA ROLE ---
class UserRole(RoleEnum):
    ADMIN = 1
    LETAN = 2
    PT = 3
    THUNGAN = 4


# --- 2. CÁC CLASS ---
class Staff(db.Model, UserMixin):
    __tablename__ = 'staff'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    role = db.Column(Enum(UserRole))
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.user_id)


class Member(db.Model, UserMixin):
    __tablename__ = 'member'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)

    def get_id(self):
        return str(self.user_id)


class GoiTap(db.Model):
    __tablename__ = 'goitap'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)


class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total_amount = db.Column(db.Float, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.user_id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('goitap.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.user_id'), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    is_paid = db.Column(db.Boolean, default=False)


class Exercises(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    muscle_group = db.Column(db.String(100))
    description = db.Column(db.Text)


class Regulation(db.Model):
    __tablename__ = 'regulation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.String(255), nullable=False)


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


        def hash_pw(p):
            return hashlib.md5(p.encode("utf-8")).hexdigest()


        # 1. TẠO TÀI KHOẢN STAFF (ADMIN, LỄ TÂN, PT)
        if not Staff.query.filter_by(username='admin').first():
            db.session.add(Staff(username="admin", password=hash_pw("123"), full_name="Quản Trị Viên",
                                 email="admin@gym.com", phone="011", role=UserRole.ADMIN))

        if not Staff.query.filter_by(username='letan').first():
            db.session.add(Staff(username="letan", password=hash_pw("123"), full_name="Lễ Tân A",
                                 email="letan@gym.com", phone="012", role=UserRole.LETAN))

        if not Staff.query.filter_by(username='pt1').first():
            db.session.add(Staff(username="pt1", password=hash_pw("123"), full_name="Huấn Luyện Viên 1",
                                 email="pt1@gym.com", phone="013", role=UserRole.PT))

        # 2. TẠO GÓI TẬP MẪU
        if not GoiTap.query.filter_by(name="Gói 1 Tháng").first():
            db.session.add_all([
                GoiTap(name="Gói 1 Tháng", duration=1, price=300000, description="Dành cho người mới"),
                GoiTap(name="Gói 6 Tháng", duration=6, price=1500000, description="Tiết kiệm 10%"),
                GoiTap(name="Gói 12 Tháng", duration=12, price=2500000, description="Chuyên nghiệp nhất")
            ])

        # 3. TẠO QUY ĐỊNH MẪU
        if not Regulation.query.first():
            db.session.add_all([
                Regulation(name='Độ tuổi tối thiểu', value='15'),
                Regulation(name='Số ngày tập tối đa/tuần', value='7')
            ])

        db.session.commit()
        print("Đã khôi phục đầy đủ tài khoản letan, pt và gói tập mẫu!")