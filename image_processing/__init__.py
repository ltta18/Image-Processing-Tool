from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_security import SQLAlchemyUserDatastore, Security

app = Flask(__name__)

app.config['SECRET_KEY'] = "linh"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from image_processing.models.model import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

from image_processing import routes

admin = Admin(app, index_view=IndexView())
admin.add_view(MyModelView(User, db.session))

security = Security(app, user_datastore)


@app.before_first_request 
def create_tables():
    db.create_all()
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='User')
    user_datastore.find_or_create_role(name='premium', description='Premium User')
    encrypted_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
    if not user_datastore.get_user('admin@gmail.com'):
        user_datastore.create_user(username="admin", email='admin@gmail.com', password=encrypted_password)
    user_datastore.add_role_to_user('admin@gmail.com', 'admin')
    user_datastore.add_role_to_user('admin@gmail.com', 'premium')
    encrypted_password_premium = bcrypt.generate_password_hash('premium123').decode('utf-8')
    if not user_datastore.get_user('premium@gmail.com'):
        user_datastore.create_user(username="premium", email='premium@gmail.com', password=encrypted_password_premium)
    user_datastore.add_role_to_user('premium@gmail.com', 'premium')
    db.session.commit()