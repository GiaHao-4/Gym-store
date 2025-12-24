from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = "ashduefj!#a" # Khóa bí mật để bảo mật session
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hao7895123@localhost/gymdb2?charset=utf8mb4" # Kết nối DB
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 3

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "login_my_user" # Trang mặc định nếu chưa đăng nhập

# Cấu hình Mail phục vụ thông báo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'haotrinh.7329@gmail.com'
app.config['MAIL_PASSWORD'] = 'kqet tcvb ocaz whvr'
app.config['MAIL_DEFAULT_SENDER'] = ('Muscle Gym System', 'haotrinh.7329@gmail.com')
mail = Mail(app)