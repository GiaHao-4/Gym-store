from datetime import datetime, timedelta
from models import db, Member, TrainingPlan, TrainingPlanDetail, Exercise
from enum import member

from flask import Flask, render_template, redirect, request, flash, url_for, jsonify
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
    exercises = Exercise.query.all()

    if request.method == 'GET':
        # Lấy danh sách hội viên để đổ vào thẻ <select>
        members = Member.query.all()
        return render_template('pt/addplan.html', members=members, exercises=exercises)

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
            db.session.flush()
            # 3. Lấy dữ liệu phần Danh sách bài tập (Dạng mảng list)
            ex_ids = request.form.getlist('exercise_id[]')
            sets_list = request.form.getlist('sets[]')
            reps_list = request.form.getlist('reps[]')
            weights_list = request.form.getlist('weight[]')
            rests_list = request.form.getlist('rest[]')

            # 4. Duyệt qua từng dòng và lưu vào TrainingPlanDetail (Bảng con)
            for i in range(len(ex_ids)):
                if not ex_ids[i]: continue

                detail = TrainingPlanDetail(
                    plan_id=new_plan.id,  # Lấy ID của kế hoạch vừa tạo ở trên
                    exercise_id=int(ex_ids[i]),
                    sets=int(sets_list[i]) if sets_list[i] else 0,
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


@app.route('/exercise')
def list_exercises():
    page = request.args.get('page', 1, type=int)
    page_size = 5
    pagination_obj = Exercise.query.order_by(Exercise.id.desc()).paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )
    return render_template('pt/exercisemanagement.html', exercises=pagination_obj)


@app.route('/exercises/add', methods=['POST'])
def add_exercise():
    if request.method == 'POST':
        try:
            new_ex = Exercise(
                name=request.form['name'],
                muscle_group=request.form['muscle_group'],
                video_link=request.form['video_link'],
                description=request.form['description']
            )
            db.session.add(new_ex)
            db.session.commit()
            flash('Thêm bài tập thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')

    return redirect(url_for('list_exercises'))


@app.route('/exercises/edit/<int:id>', methods=['POST'])
def edit_exercise(id):
    ex = Exercise.query.get_or_404(id)
    if request.method == 'POST':
        try:
            ex.name = request.form['name']
            ex.muscle_group = request.form['muscle_group']
            ex.video_link = request.form['video_link']
            ex.description = request.form['description']

            db.session.commit()
            flash('Cập nhật thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi cập nhật: {str(e)}', 'danger')

    return redirect(url_for('list_exercises'))


@app.route('/exercises/delete/<int:id>', methods=['POST'])
def delete_exercise(id):
    ex = Exercise.query.get_or_404(id)
    try:
        db.session.delete(ex)
        db.session.commit()
        flash('Đã xóa bài tập!', 'success')
    except Exception as e:
        flash('Bài tập hiện đang được thêm trong lịch tập! Bạn không thể xóa!', 'danger')

    return redirect(url_for('list_exercises'))


@app.route('/schedule')
def view_schedule():
    # Lấy danh sách hội viên để đổ vào Dropdown lọc
    members = Member.query.all()
    return render_template('pt/schedule.html', members=members)


@app.route('/api/schedule-events')
def get_schedule_events():
    # FullCalendar gửi lên start và end dạng chuỗi ISO (VD: '2025-12-01T00:00:00')
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    member_filter = request.args.get('member_id')

    # Xử lý chuỗi ngày tháng từ request để query DB
    # (Vì DB lưu Date riêng, Time riêng nên ta filter theo Date)
    try:
        start_date = datetime.fromisoformat(start_str).date()
        end_date = datetime.fromisoformat(end_str).date()
    except:
        return jsonify([])  # Trả về rỗng nếu lỗi ngày tháng

    # Query cơ bản: Lấy theo ngày
    query = TrainingPlan.query.filter(
        TrainingPlan.training_date >= start_date,
        TrainingPlan.training_date <= end_date
    )

    # Nếu có chọn bộ lọc hội viên
    if member_filter and member_filter != 'all':
        try:
            # Ép kiểu sang số nguyên (int) để so sánh chính xác với Database
            member_id_int = int(member_filter)
            query = query.filter(TrainingPlan.member_id == member_id_int)
        except ValueError:
            pass
    plans = query.all()

    events_list = []

    for plan in plans:
        # 1. Ghép Ngày + Giờ để tạo thành 'start' (datetime)
        start_dt = datetime.combine(plan.training_date, plan.training_time)

        # 2. Giả định mỗi buổi tập kéo dài 60 phút (Vì DB bạn không có cột end_time)
        end_dt = start_dt + timedelta(minutes=60)

        # 3. Lấy danh sách bài tập chi tiết
        exercises_names = []
        for detail in plan.details:
            # detail.exercise đã được define trong model của bạn, nên gọi .name được luôn
            if detail.exercise:
                exercises_names.append(detail.exercise.name)

        # 4. Xác định màu sắc dựa trên status
        color_class = 'fc-event-pending'  # Mặc định xanh dương
        if plan.status == 'completed':
            color_class = 'fc-event-completed'  # Xanh lá
        elif plan.status == 'cancelled':
            color_class = 'fc-event-cancelled'  # Đỏ

        # 5. Tạo Dictionary dữ liệu
        event_dict = {
            'id': plan.id,
            'title': f"{plan.member.full_name}",  # Tiêu đề hiển thị trên lịch
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'className': color_class,
            'extendedProps': {
                'memberName': plan.member.full_name,
                'status': plan.status if plan.status else 'pending',
                'exercises': exercises_names,
                'note': plan.note
            }
        }
        events_list.append(event_dict)

    return jsonify(events_list)


@login.user_loader
def get_user(id):
    return dao.get_user_by_id(id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
