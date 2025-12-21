from datetime import datetime
from models import db, Member, TrainingPlan, TrainingPlanDetail
from enum import member

from flask import Flask, render_template, redirect, request, flash, url_for
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
        role = request.form.get('role')
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

@app.route('/addplan', methods=['GET', 'POST'])
def addplan():
    if request.method == 'GET':
        # Lấy danh sách hội viên để đổ vào thẻ <select>
        members = Member.query.all()
        return render_template('pt/addplan.html', members=members)

    if request.method == 'POST':
        try:
            # 1. Lấy dữ liệu phần Thông tin chung
            member_id = request.form.get('member_id')
            date_str = request.form.get('training_date')
            time_str = request.form.get('training_time')
            note = request.form.get('note')

            # Kiểm tra ngay lập tức. Nếu thiếu thì đuổi về, không cho chạy tiếp.
            if not date_str or not time_str or not member_id:
                flash('Vui lòng điền đầy đủ thông tin!', 'warning')
                return redirect(url_for('addplan'))

            # Convert chuỗi ngày giờ sang định dạng Python
            t_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            t_time = datetime.strptime(time_str, '%H:%M').time()

            # 2. Lưu vào bảng TrainingPlan (Bảng cha)
            new_plan = TrainingPlan(
                member_id=member_id,
                training_date=t_date,
                training_time=t_time,
                note=note
            )
            db.session.add(new_plan)
            db.session.flush()  # flush để database tạo ID cho new_plan ngay lập tức (dù chưa commit)

            # 3. Lấy dữ liệu phần Danh sách bài tập (Dạng mảng list)
            ex_names = request.form.getlist(
                'exercise_id[]')  # Lưu ý: HTML bạn đặt là exercise_id[] nhưng value là tên viết tắt
            sets_list = request.form.getlist('sets[]')
            reps_list = request.form.getlist('reps[]')
            weights_list = request.form.getlist('weight[]')
            rests_list = request.form.getlist('rest[]')

            # 4. Duyệt qua từng dòng và lưu vào TrainingPlanDetail (Bảng con)
            for i in range(len(ex_names)):
                detail = TrainingPlanDetail(
                    plan_id=new_plan.id,  # Lấy ID của kế hoạch vừa tạo ở trên
                    exercise_name=ex_names[i],
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weights_list[i]) if weights_list[i] else 0,
                    rest_time=int(rests_list[i])
                )
                db.session.add(detail)

            # 5. Chốt đơn - Lưu tất cả vào DB
            db.session.commit()
            flash('Tạo kế hoạch thành công!', 'success')
            return redirect(url_for('addplan'))

        except Exception as e:
            db.session.rollback()  # Nếu lỗi thì hoàn tác
            print(f"Lỗi: {e}")
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('addplan'))


@login.user_loader
def get_user(id):
    return dao.get_user_by_id(id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
