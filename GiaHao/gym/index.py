from datetime import datetime, timedelta
from flask import render_template, redirect, request, flash, url_for, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message

# --- 1. IMPORT CẤU HÌNH TỪ PACKAGE GYM ---
from gym import app, db, dao, login, mail

# --- 2. IMPORT MODEL TỪ GYM.MODELS (CHỈ DÙNG 1 CÁCH DUY NHẤT) ---
# Lưu ý: 'Exercise' là tên class trong models.py (không có s)
from gym.models import UserRole, Exercise, GoiTap, Receipt, Member, TrainingPlan, TrainingPlanDetail, Staff, Regulation


# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(int(user_id))


@app.route('/')
def index():
    packages = GoiTap.query.limit(3).all()
    return render_template("index.html", packages=packages)


# ==========================================
# XÁC THỰC NGƯỜI DÙNG (LOGIN / LOGOUT)
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = dao.auth_user(username, password, role)

        if user:
            login_user(user)
            return redirect('/reception' if str(user.role) == 'UserRole.LETAN' else '/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không chính xác!"

    return render_template("login.html", err_msg=err_msg)


@app.route('/logout')
def logout_by_user():
    logout_user()
    return redirect('/login')


# ==========================================
# QUẢN LÝ STAFF (ADMIN)
# ==========================================
@app.route("/admin/staff", methods=['GET', 'POST'])
@login_required
def manage_staff():
    if current_user.role != UserRole.ADMIN:
        return redirect('/')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            dao.add_staff(
                username=request.form.get('username'), password=request.form.get('password'),
                name=request.form.get('name'), email=request.form.get('email'),
                phone=request.form.get('phone'), role_name=request.form.get('role')
            )
            flash("Thêm nhân viên thành công!", "success")
        elif action == 'edit':
            dao.update_staff(
                staff_id=request.form.get('staff_id'), name=request.form.get('name'),
                email=request.form.get('email'), phone=request.form.get('phone'),
                role_name=request.form.get('role')
            )
            flash("Cập nhật thông tin thành công!", "info")
        elif action == 'toggle':
            dao.toggle_staff_status(request.form.get('staff_id'))
            return redirect(url_for('manage_staff'))
        return redirect(url_for('manage_staff'))

    staff_list = dao.get_all_staff()
    return render_template('admin/staff.html', staff_list=staff_list)


# ==========================================
# CHỨC NĂNG CỦA PT (HUẤN LUYỆN VIÊN)
# ==========================================

@app.route('/addplan', methods=['GET', 'POST'])
@login_required
def addplan():
    # Kiểm tra quyền: Chỉ PT hoặc Admin
    # Lưu ý: Cần đảm bảo so sánh đúng với Enum hoặc giá trị trong DB
    if current_user.role != UserRole.PT and current_user.role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect('/')

    exercises = Exercise.query.all()

    if request.method == 'GET':
        members = Member.query.all()
        return render_template('pt/addplan.html', members=members, exercises=exercises)

    if request.method == 'POST':
        try:
            member_id = request.form.get('member_id')
            date_str = request.form.get('training_date')
            time_str = request.form.get('training_time')
            note = request.form.get('note')

            if not date_str or not time_str or not member_id:
                flash('Vui lòng điền đầy đủ thông tin!', 'warning')
                return redirect(url_for('addplan'))

            t_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            t_time = datetime.strptime(time_str, '%H:%M').time()

            new_plan = TrainingPlan(
                member_id=member_id,
                training_date=t_date,
                training_time=t_time,
                note=note
            )
            db.session.add(new_plan)
            db.session.flush()

            ex_ids = request.form.getlist('exercise_id[]')
            sets_list = request.form.getlist('sets[]')
            reps_list = request.form.getlist('reps[]')
            weights_list = request.form.getlist('weight[]')
            rests_list = request.form.getlist('rest[]')

            for i in range(len(ex_ids)):
                if not ex_ids[i]: continue

                detail = TrainingPlanDetail(
                    plan_id=new_plan.id,
                    exercise_id=int(ex_ids[i]),
                    sets=int(sets_list[i]) if sets_list[i] else 0,
                    reps=int(reps_list[i]),
                    weight=float(weights_list[i]) if weights_list[i] else 0,
                    rest_time=int(rests_list[i])
                )
                db.session.add(detail)

            db.session.commit()
            flash('Tạo kế hoạch thành công!', 'success')
            return redirect(url_for('addplan'))

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi: {e}")
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('addplan'))


@app.route('/exercise')
def list_exercises():
    page = request.args.get('page', 1, type=int)
    page_size = 5
    # Sửa Exercises -> Exercise (đúng tên class model)
    pagination_obj = Exercise.query.order_by(Exercise.id.desc()).paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )
    return render_template('pt/exercisemanagement.html', exercises=pagination_obj)


@app.route('/exercises/add', methods=['POST'])
@login_required
def add_exercise():
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
@login_required
def edit_exercise(id):
    ex = Exercise.query.get_or_404(id)
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
@login_required
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
@login_required
def view_schedule():
    members = Member.query.all()
    return render_template('pt/schedule.html', members=members)


@app.route('/api/schedule-events')
def get_schedule_events():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    member_filter = request.args.get('member_id')

    try:
        start_date = datetime.fromisoformat(start_str).date()
        end_date = datetime.fromisoformat(end_str).date()
    except:
        return jsonify([])

    query = TrainingPlan.query.filter(
        TrainingPlan.training_date >= start_date,
        TrainingPlan.training_date <= end_date
    )

    if member_filter and member_filter != 'all':
        try:
            member_id_int = int(member_filter)
            query = query.filter(TrainingPlan.member_id == member_id_int)
        except ValueError:
            pass
    plans = query.all()

    events_list = []
    for plan in plans:
        start_dt = datetime.combine(plan.training_date, plan.training_time)
        end_dt = start_dt + timedelta(minutes=60)

        exercises_names = []
        for detail in plan.details:
            if detail.exercise:
                exercises_names.append(detail.exercise.name)

        color_class = 'fc-event-pending'
        if plan.status == 'completed':
            color_class = 'fc-event-completed'
        elif plan.status == 'cancelled':
            color_class = 'fc-event-cancelled'

        event_dict = {
            'id': plan.id,
            'title': f"{plan.member.full_name}",
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


# ==========================================
# QUY TRÌNH ĐĂNG KÝ (BOOKING CLIENT)
# ==========================================

@app.route('/booking', methods=['GET', 'POST'])
def booking_step1():
    if request.method == 'POST':
        phone = request.form.get('phone')
        user = Member.query.filter_by(phone=phone).first()
        session['booking_phone'] = phone
        if user:
            session['booking_user_id'] = user.user_id
            session['booking_type'] = 'RENEW'
            return redirect('/booking/select-package')
        else:
            session['booking_type'] = 'NEW'
            return redirect('/booking/register-info')
    return render_template('client/step1_check_phone.html')


@app.route('/booking/register-info', methods=['GET', 'POST'])
def booking_new_member():
    if request.method == 'POST':
        session['new_user_info'] = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
        }
        return redirect('/booking/select-package')
    phone = session.get('booking_phone')
    return render_template('client/step2_register.html', phone=phone)


@app.route('/booking/select-package')
def booking_select_package():
    packages = GoiTap.query.all()
    return render_template('client/step3_packages.html', packages=packages)


@app.route('/booking/payment')
def booking_payment():
    package_id = request.args.get('package_id')
    package = GoiTap.query.get(package_id)
    session['selected_package_id'] = package_id
    user_info = {}

    if session.get('booking_type') == 'NEW':
        user_info = session.get('new_user_info')
        user_info['phone'] = session.get('booking_phone')
        user_info['type'] = 'Khách hàng mới'
    else:
        user = Member.query.get(session.get('booking_user_id'))
        user_info['name'] = user.full_name
        user_info['phone'] = user.phone
        user_info['type'] = 'Hội viên cũ'

    return render_template('client/step4_payment.html', package=package, user=user_info)


@app.route('/booking/complete', methods=['POST'])
def booking_complete():
    try:
        booking_type = session.get('booking_type')
        package_id = session.get('selected_package_id')
        package = GoiTap.query.get(package_id)

        user_id = None
        if booking_type == 'NEW':
            info = session.get('new_user_info')
            phone = session.get('booking_phone')
            new_user = Member(full_name=info['name'], email=info['email'], phone=phone)
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.user_id
        else:
            user_id = session.get('booking_user_id')

        receipt = Receipt(
            total_amount=package.price,
            member_id=user_id,
            package_id=package_id,
            staff_id=None,
            is_paid=True
        )
        db.session.add(receipt)
        db.session.commit()

        try:
            # Sửa lỗi logic: package.duration là số ngày, không cần nhân 30 nếu đơn vị là ngày
            expire_date = datetime.now() + timedelta(days=package.duration)

            expire_str = expire_date.strftime("%d/%m/%Y")
            created_str = datetime.now().strftime("%d/%m/%Y %H:%M")

            user_email = info['email'] if booking_type == 'NEW' else Member.query.get(user_id).email
            user_name = info['name'] if booking_type == 'NEW' else Member.query.get(user_id).full_name

            subject = "XÁC NHẬN THANH TOÁN THÀNH CÔNG - MUSCLE GYM"
            msg = Message(subject, recipients=[user_email])
            msg.html = f"""
                        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd;">
                            <h2 style="color: #28a745;">THANH TOÁN THÀNH CÔNG!</h2>
                            <p>Xin chào <strong>{user_name}</strong>,</p>
                            <p>Cảm ơn bạn đã đăng ký dịch vụ tại Muscle Gym.</p>
                            <p>Gói tập: <strong>{package.name}</strong></p>
                            <p>Ngày hết hạn: <strong>{expire_str}</strong></p>
                        </div>
                        """
            mail.send(msg)
            print("Đã gửi email thành công!")
        except Exception as e:
            print(f"Lỗi gửi email: {str(e)}")

        session.clear()
        return render_template('client/success.html')
    except Exception as e:
        return f"Có lỗi xảy ra: {str(e)}"


# ==========================================
# CÁC ROUTE ADMIN KHÁC (GIỮ NGUYÊN HOẶC THÊM NẾU CẦN)
# ==========================================
# (Phần Regulation và Stats bạn có thể giữ nguyên nếu dao hỗ trợ)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5000)