import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'GSDG%67&*&)+()&&vbb*&'
	MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
	MAIL_PORT = int(os.environ.get('MAIL_PORT', ' 465'))
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
	MAIL_USE_SSL = True
	SSL_REDIRECT = False
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '479260115@qq.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'dtqoehgzpkuibgcg'
	
	MAIL_DEFAULT_SENDER = '479260115@qq.com'

	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WHYBLOG_ADMIN = os.environ.get('WHYBLOG_ADMIN') or '479260115@qq.com'


	#每页显示文章数量
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class HerokuConfig(ProductionConfig):
	pass


config = {
	'developmentconfig':DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

	'default':DevelopmentConfig
}
