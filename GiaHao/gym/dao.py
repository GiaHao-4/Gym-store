import hashlib
from datetime import datetime
from sqlalchemy import func, extract
from gym import app, db
from gym.models import Staff, Member, GoiTap, Exercises, Regulation, Receipt, UserRole


# ==========================================
# 1. XÁC THỰC NGƯỜI DÙNG
# ==========================================
def get_user_by_id(user_id):
    """Lấy user theo ID (Giữ nguyên)"""
    return Staff.query.get(int(user_id))


def auth_user(username, password, role_name):
    """Xác thực người dùng (Giữ nguyên logic MD5)"""
    username = username.strip()
    password = password.strip()
    password_hashed = hashlib.md5(password.encode("utf-8")).hexdigest()

    try:
        if isinstance(role_name, str):
            role_enum = UserRole[role_name]
        else:
            role_enum = role_name
    except KeyError:
        return None

    return Staff.query.filter(
        Staff.username == username,
        Staff.password == password_hashed,
        Staff.role == role_enum,
        Staff.is_active == True
    ).first()


# ==========================================
# 2. QUẢN LÝ NHÂN VIÊN (STAFF)
# ==========================================

def get_all_staff():
    """Lấy danh sách tất cả nhân viên (Giữ nguyên)"""
    return Staff.query.all()


def add_staff(username, password, name, email, phone, role_name):
    """Thêm nhân viên mới"""
    pw_hash = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    role_enum = UserRole[role_name] if isinstance(role_name, str) else role_name

    new_staff = Staff(
        username=username.strip(),
        password=pw_hash,
        full_name=name,
        email=email,
        phone=phone,
        role=role_enum,
        is_active=True
    )
    db.session.add(new_staff)
    db.session.commit()
    return True


def update_staff(staff_id, name, email, phone, role_name):
    """Cập nhật thông tin nhân viên (Giữ nguyên)"""
    s = Staff.query.get(staff_id)
    if s:
        s.full_name = name
        s.email = email
        s.phone = phone
        if isinstance(role_name, str):
            s.role = UserRole[role_name]
        else:
            s.role = role_name
        db.session.commit()
        return True
    return False


def toggle_staff_status(staff_id):
    """Khóa hoặc mở khóa tài khoản"""
    s = Staff.query.get(staff_id)
    if s:
        s.is_active = not s.is_active
        db.session.commit()
        return True
    return False


# ==========================================
# 3. QUẢN LÝ GÓI TẬP (PACKAGES)
# ==========================================

def get_goitap(kw=None):
    """Lấy danh sách gói tập (Giữ nguyên)"""
    query = GoiTap.query
    if kw:
        query = query.filter(GoiTap.name.contains(kw))
    return query.all()


def add_package(name, duration, price, description=None):
    """Thêm gói tập (Đồng bộ tên hàm với index.py)"""
    p = GoiTap(name=name, duration=duration, price=price, description=description)
    db.session.add(p)
    db.session.commit()
    return True


def delete_goitap(goitap_id):
    """Xóa gói tập (Giữ nguyên)"""
    p = GoiTap.query.get(goitap_id)
    if p:
        db.session.delete(p)
        db.session.commit()
        return True
    return False


def update_package(p_id, name, price):
    """Cập nhật tên và giá gói tập (Giữ nguyên bản cuối của bạn)"""
    p = GoiTap.query.get(p_id)
    if p:
        p.name = name
        p.price = price
        db.session.commit()
        return True
    return False


# ==========================================
# 4. QUẢN LÝ BÀI TẬP (EXERCISES)
# ==========================================

def get_exercises(kw=None):
    query = Exercises.query
    if kw:
        query = query.filter(Exercises.name.contains(kw))
    return query.all()


def add_exercise(name, description=None, muscle_group="Toàn thân"):
    """Thêm bài tập mới"""
    ex = Exercises(name=name, muscle_group=muscle_group, description=description)
    db.session.add(ex)
    db.session.commit()
    return True


def update_exercise(ex_id, name, muscle_group, description):
    """Cập nhật bài tập (Đảm bảo nhận đủ 4 tham số từ HTML)"""
    ex = Exercises.query.get(ex_id)
    if ex:
        ex.name = name
        ex.muscle_group = muscle_group
        ex.description = description
        db.session.commit()
        return True
    return False


def delete_exercise(ex_id):
    ex = Exercises.query.get(ex_id)
    if ex:
        db.session.delete(ex)
        db.session.commit()
        return True
    return False


# ==========================================
# 5. QUẢN LÝ QUY ĐỊNH (REGULATIONS)
# ==========================================

def get_regulations():
    """Lấy quy định (Giữ nguyên)"""
    return Regulation.query.all()


def update_regulation(reg_id, new_value):
    """Cập nhật quy định (Giữ nguyên)"""
    reg = Regulation.query.get(reg_id)
    if reg:
        reg.value = new_value
        db.session.commit()
        return True
    return False


# ==========================================
# 6. BÁO CÁO & THỐNG KÊ (REPORTS)
# ==========================================

def count_new_members_by_month(year):
    """Thống kê hội viên mới (Giữ nguyên)"""
    return db.session.query(
        extract('month', Receipt.created_date),
        func.count(Receipt.member_id)
    ).filter(
        extract('year', Receipt.created_date) == year
    ).group_by(
        extract('month', Receipt.created_date)
    ).order_by(
        extract('month', Receipt.created_date)
    ).all()


def revenue_stats_by_month(year):
    """Doanh thu tháng (Giữ nguyên)"""
    return db.session.query(
        extract('month', Receipt.created_date),
        func.sum(Receipt.total_amount)
    ).filter(
        extract('year', Receipt.created_date) == year,
        Receipt.is_paid == True
    ).group_by(
        extract('month', Receipt.created_date)
    ).order_by(
        extract('month', Receipt.created_date)
    ).all()


def revenue_stats_by_package(kw=None, from_date=None, to_date=None):
    """Thống kê theo gói (Requirement 4)"""
    query = db.session.query(GoiTap.id, GoiTap.name, func.sum(Receipt.total_amount)) \
        .join(Receipt, GoiTap.id == Receipt.package_id)
    if kw: query = query.filter(GoiTap.name.contains(kw))
    if from_date: query = query.filter(Receipt.created_date >= from_date)
    if to_date: query = query.filter(Receipt.created_date <= to_date)
    return query.group_by(GoiTap.id).all()


def get_active_member_list():
    """Hội viên còn hạn (Giữ nguyên)"""
    now = datetime.now()
    return db.session.query(Member, Receipt, GoiTap) \
        .join(Receipt, Member.user_id == Receipt.member_id) \
        .join(GoiTap, Receipt.package_id == GoiTap.id) \
        .filter(func.adddate(Receipt.created_date, GoiTap.duration * 30) >= now).all()


# ==========================================
# 7. QUẢN LÝ HỘI VIÊN (BỔ SUNG CHO BOOKING FLOW)
# ==========================================

def get_member_by_phone(phone):
    """Tìm hội viên theo số điện thoại (Dùng cho Booking Step 1)"""
    return Member.query.filter_by(phone=phone.strip()).first()


def add_member(name, email, phone):
    """Thêm hội viên mới khi đăng ký (Dùng cho Booking Step 2)"""
    m = Member(full_name=name.strip(), email=email.strip(), phone=phone.strip())
    db.session.add(m)
    db.session.commit()
    return m


def add_receipt(member_id, package_id, total_amount, staff_id=None):
    """Tạo hóa đơn khi thanh toán thành công (Dùng cho Booking Confirm)"""
    r = Receipt(
        member_id=member_id,
        package_id=package_id,
        total_amount=total_amount,
        staff_id=staff_id,
        created_date=datetime.now(),
        is_paid=True
    )
    db.session.add(r)
    db.session.commit()
    return True


# --- ĐÃ KHÔI PHỤC DÒNG CODE TEST THEO YÊU CẦU ---
if __name__ == "__main__":
    with app.app_context():
        # Kiểm tra xác thực admin
        print("Test Auth Admin:", auth_user("admin", "123", UserRole.ADMIN))