import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = 'GSDG%67&*&)+()&&vbb*&'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	WHYBLOG_ADMIN = '479260115@qq.com'
	#每页显示文章数量
	WHY_POSTS_PER_PAGE =  8
	WHY_COMMENTS_PER_PAGE =  8
	WHY_FOLLOWERS_PER_PAGE =  15

	@staticmethod
	def init_app(app):
		pass




class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	MAIL_USERNAME = '479260115@qq.com'
	MAIL_PASSWORD = 'dtqoehgzpkuibgcg'
	MAIL_DEFAULT_SENDER = '479260115@qq.com'



config = {
	'developmentconfig':DevelopmentConfig,
	'default':DevelopmentConfig
}