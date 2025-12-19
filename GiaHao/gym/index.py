from flask import Flask, render_template, redirect, request
from flask_login import current_user, login_user, logout_user

from gym import dao, login, reception
from gym import app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = None

    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        role=request.form.get('role')
        print(username, password, role)
        user = dao.auth_user(username, password, role)
        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng"
    return render_template("login.html", err_msg=err_msg)
@app.route('/logout')
def logout_by_user():
    logout_user()
    return redirect('/login')
# @app.route('/reception')
# def reception():
#     return render_template('letan/index.html')
@login.user_loader
def get_user(id):
    return dao.get_user_by_id(id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)