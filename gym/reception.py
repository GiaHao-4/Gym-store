from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.theme import Bootstrap4Theme
from flask import request, redirect, flash
from markupsafe import Markup
from flask_login import current_user

# SỬA IMPORT QUAN TRỌNG TẠI ĐÂY:
from gym.models import Member, GoiTap, Receipt,UserRole
from gym import app, db


class MyUserView(ModelView):
    column_list = ['full_name', 'email', 'phone', 'Gia Hạn']
    column_searchable_list = ['full_name', 'phone']
    column_labels = dict(full_name='Tên', phone='SĐT')

    def _format_renew_btn(view, context, model, name):
        renew_url = f"/reception/renew-flow?user_id={model.user_id}"
        return Markup(f'''
            <a href="{renew_url}" class="btn btn-success btn-sm text-white font-weight-bold">
                <i class="fas fa-cart-plus"></i> Gia hạn
            </a>
        ''')

    column_formatters = {
        'Gia Hạn': _format_renew_btn
    }


class MyIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> str:
        # Lưu ý: Bạn cần đảm bảo file templates/letan/index.html tồn tại
        return self.render('letan/index.html')

    @expose('/register-flow')
    def register_flow(self):
        packages = GoiTap.query.all()
        return self.render('letan/packages.html', packages=packages)

    @expose('/renew-flow')
    def process_renewal(self):
        user_id = request.args.get('user_id')
        user = Member.query.get(user_id)
        packages = GoiTap.query.all()
        return self.render('letan/packages.html', packages=packages, user_to_renew=user)

    @expose('/process-renewal')
    def process_renew(self):
        user_id = request.args.get('user_id')
        package_id = request.args.get('package_id')
        if not user_id or not package_id:
            flash('Lỗi: Thiếu thông tin!', 'error')
            return redirect('/reception/member')
        try:
            package = GoiTap.query.get(package_id)
            receipt = Receipt(total_amount=package.price, member_id=user_id, package_id=package_id,
                              staff_id=current_user.user_id)
            db.session.add(receipt)
            db.session.commit()
            flash(f'Đã gia hạn gói "{package.name}"!', 'success')
        except Exception as ex:
            flash(f'Lỗi: {str(ex)}', 'error')
        return redirect('/reception/member')

    @expose('/register-member', methods=('GET', 'POST'))
    def register_member(self):
        package_id = request.args.get('package_id')
        if not package_id:
            return redirect('/reception/register-flow')
        package = GoiTap.query.get(package_id)
        err_msg = ""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            try:
                # Tạo member không cần pass (theo logic bạn kia)
                member = Member(full_name=name, email=email, phone=phone)
                db.session.add(member)
                db.session.commit()

                receipt = Receipt(total_amount=package.price, member_id=member.user_id, package_id=package.id,
                                  staff_id=current_user.user_id)
                db.session.add(receipt)
                db.session.commit()
                flash("Đã thêm hội viên thành công!", 'success')
                return redirect('/reception/member')
            except Exception as e:
                err_msg = f"Lỗi: {str(e)}"
        return self.render('letan/register_user.html', package=package, err_msg=err_msg)


# Khởi tạo Admin Lễ Tân
reception = Admin(app=app, name='Reception', url='/reception', theme=Bootstrap4Theme(),
                  index_view=MyIndexView(name='Trang chủ', url='/reception'))
reception.add_view(MyUserView(Member, db.session))