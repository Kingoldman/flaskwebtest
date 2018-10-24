from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
import flask_whooshalchemyplus

moment = Moment()
db = SQLAlchemy()
bootstrap = Bootstrap()
loginmanager = LoginManager()
loginmanager.session_protection = 'strong'
loginmanager.login_view ='auth.login'
mail = Mail()
pagedown = PageDown()




def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	moment.init_app(app)
	db.init_app(app)
	bootstrap.init_app(app)
	loginmanager.init_app(app)
	mail.init_app(app)
	pagedown.init_app(app)
	flask_whooshalchemyplus.init_app(app)

	#把所有请求重定向到安全http
	if not app.config['SSL_DISABLE']:
		from flask_sslify import SSLify
		sslify = SSLify(app)

	from .main import main
	app.register_blueprint(main)
	from .auth import auth
	app.register_blueprint(auth,url_prefix = '/auth')


	return app