from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sqlite3

db = SQLAlchemy()
conn = sqlite3.connect('requests.db', check_same_thread=False)
c = conn.cursor()

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = 'bigchungus'
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	db.init_app(app)

	login_manager = LoginManager()
	login_manager.login_view = 'main.index'
	login_manager.init_app(app)

	from .models import User

	@login_manager.user_loader
	def load_user(user_email):
		return User.query.get(user_email)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app