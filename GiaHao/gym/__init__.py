from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from flask_mail import Mail
app=Flask(__name__)
app.secret_key="ashduefj!#a"
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:hao7895123@localhost/gymdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 3
db = SQLAlchemy(app)
login = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'haotrinh.7329@gmail.com' # Thay email của bạn
app.config['MAIL_PASSWORD'] = 'kqet tcvb ocaz whvr'     # Thay bằng Mật khẩu ứng dụng 16 ký tự
app.config['MAIL_DEFAULT_SENDER'] = ('Muscle Gym System', 'email_cua_ban@gmail.com')
mail = Mail(app)