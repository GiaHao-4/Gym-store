from flask import Flask, render_template, redirect, request, session
from flask_login import current_user, login_user, logout_user
from flask_mail import Message

from gym import dao, login, reception, db
from gym import app, mail
from gym.models import Member, GoiTap, Receipt
from datetime import datetime, timedelta


@app.route('/')
def index():
    packages = GoiTap.query.limit(3).all()
    return render_template("index.html", packages=packages)

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
@app.route('/booking', methods=['GET', 'POST'])
def booking_step1():
    if request.method.__eq__('POST'):
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

        receipt = Receipt(total_amount=package.price, member_id=user_id, package_id=package_id, staff_id=None, is_paid=True)
        db.session.add(receipt)
        db.session.commit()
        try:
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
                            <p>Cảm ơn bạn đã đăng ký dịch vụ tại Muscle Gym. Dưới đây là thông tin hóa đơn của bạn:</p>
    
                            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                                <tr style="background-color: #f8f9fa;">
                                    <td style="padding: 10px; border: 1px solid #ddd;">Gói tập:</td>
                                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{package.name}</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #ddd;">Tổng tiền:</td>
                                    <td style="padding: 10px; border: 1px solid #ddd; color: #d9534f;">
                                        <strong>{"{:,.0f}".format(package.price)} VNĐ</strong>
                                    </td>
                                </tr>
                                <tr style="background-color: #f8f9fa;">
                                    <td style="padding: 10px; border: 1px solid #ddd;">Ngày đăng ký:</td>
                                    <td style="padding: 10px; border: 1px solid #ddd;">{created_str}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #ddd;">Ngày hết hạn:</td>
                                    <td style="padding: 10px; border: 1px solid #ddd; color: #007bff; font-weight: bold;">
                                        {expire_str}
                                    </td>
                                </tr>
                            </table>
    
                            <p style="margin-top: 20px;">Vui lòng xuất trình email này tại quầy lễ tân để nhận thẻ tập.</p>
                            <p>Chúc bạn có những giờ phút tập luyện hiệu quả!</p>
                            <hr>
                            <small>Muscle Gym System - Auto Reply</small>
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
@login.user_loader
def get_user(id):
    return dao.get_user_by_id(id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)