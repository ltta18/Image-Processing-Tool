from image_processing import db, login_manager
from flask_login import UserMixin
from flask_security import RoleMixin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from flask import render_template, request
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

roles_users = db.Table('roles_users',
                        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))
                        
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(20), nullable=False)
    date_processed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __str__(self):
        return self.filename

    def __hash__(self):
        return hash(self.filename)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_image = db.relationship('Image', backref="users")
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary="roles_users", backref=db.backref('users', lazy="dynamic"))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def is_active(self):
        return self.active
    
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

#Admin view
class MyBaseView(object):
    column_editable_list = ['username', 'email','roles']
    column_exclude_list = ('password')
    column_searchable_list = ['username']
    def is_accessible(self):
        return current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return render_template('error.html', title="Authentication Error", message="Only admin can access this source.", route="/")

class MyModelView(MyBaseView, ModelView):
    column_display_all_relations = True
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.roles = 'user'
    pass

class IndexView(MyBaseView, AdminIndexView):
    pass

