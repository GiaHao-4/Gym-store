from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.theme import Bootstrap4Theme
from flask import request, redirect, flash
from models import Member, GoiTap, Receipt
from gym import app, db
from flask_login import current_user

class MyUserView(ModelView):
    column_searchable_list=['full_name', 'phone']
    column_labels = dict(full_name='Tên', phone='SĐT')

class MyIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> str:
        return self.render('letan/index.html')

    @expose('/register-flow')
    def register_flow(self):
        packages=GoiTap.query.all()
        return self.render('letan/packages.html', packages=packages)

    @expose('/register-member', methods=('GET', 'POST'))
    def register_member(self):
        package_id=request.args.get('package_id')
        if not package_id:
            return redirect('/reception/register-flow')
        package=GoiTap.query.get(package_id)
        err_msg=""
        if request.method=='POST':
            name=request.form.get('name')
            email=request.form.get('email')
            phone=request.form.get('phone')
            try:
                member=Member(full_name=name, email=email, phone=phone)
                db.session.add(member)
                db.session.commit()
                receipt=Receipt(total_amount=package.price, member_id=member.user_id, package_id=package.id, staff_id=current_user.user_id)
                db.session.add(receipt)
                db.session.commit()
                flash("Đã thêm hội viên và tạo phiếu đăng ký thành công!", 'success')
                return redirect('/reception/member')
            except Exception as e:
                err_msg=f"Có lỗi xảy ra: {str(e)}"
        return self.render('letan/register_user.html', package=package, err_msg=err_msg)

reception=Admin(app=app, name='Reception', url='/reception', theme=Bootstrap4Theme(), index_view=MyIndexView(name='Trang chủ', url='/reception'))

reception.add_view(MyUserView(Member, db.session))