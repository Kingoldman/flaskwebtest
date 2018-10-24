import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'GSDG%67&*&)+()&&vbb*&'
	
	MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
	MAIL_PORT = os.environ.get('MAIL_PORT') or 465
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '479260115@qq.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'dtqoehgzpkuibgcg'
	MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or '479260115@qq.com'
	

	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	WHYBLOG_ADMIN = os.environ.get('WHYBLOG_ADMIN') or '479260115@qq.com'
	
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	SSL_DISABLE = True

	#每页显示数量
	WHY_POSTS_PER_PAGE =  8
	WHY_COMMENTS_PER_PAGE =  8
	WHY_FOLLOWERS_PER_PAGE =  15

	@staticmethod
	def init_app(app):
		pass




class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data.sqlite')

	
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data.sqlite')
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)

class HerokuConfig(ProductionConfig):
	SSL_DISABLE = bool( os.environ.get('SSL_DISABLE'))
	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app(app)

		#处理代理服务器首部
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)

		#错误日志
		import logging
		from logging import StreamHandler
		file_handler = StreamHandler()
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)


config = {
	'developmentconfig':DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

	'default':DevelopmentConfig
}
