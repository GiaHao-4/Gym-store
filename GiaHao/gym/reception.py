from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.theme import Bootstrap4Theme

from models import Member
from gym import app, db

class MyUserView(ModelView):
    column_searchable_list=['full_name', 'phone']
    column_labels = dict(full_name='Tên', phone='SĐT')

class MyIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> str:
        return self.render('letan/index.html')

reception=Admin(app=app, name='Reception', url='/reception', theme=Bootstrap4Theme(), index_view=MyIndexView(name='Trang chủ', url='/reception'))

reception.add_view(MyUserView(Member, db.session))