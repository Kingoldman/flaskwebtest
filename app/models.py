
from .__init__ import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from app import loginmanager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from datetime import datetime
import hashlib
import bleach
from markdown import markdown

class User(UserMixin,db.Model):
	__tablename__ ='users'
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(64),unique = True,index = True)
	email = db.Column(db.String(128),unique = True,index = True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean,default = False)

	#资料信息
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(),default = datetime.utcnow())
	last_seen = db.Column(db.DateTime(),default =datetime.utcnow())
	avatar_hash = db.Column(db.String(32))
	posts = db.relationship('Post',backref = 'author',lazy = 'dynamic')

	is_administrator = db.Column(db.Boolean,default = False,index = True)

	comments = db.relationship('Comment',backref = 'author',lazy = 'dynamic')

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		#Roel--backref = 'role'
		if self.email == current_app.config['WHYBLOG_ADMIN']:
			self.is_administrator = True

		#模型初始化计算散列值
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

	def can(self):
		if self.is_administrator:
			return True

	def gravatar(self,size = 100,default = 'identicon',rating = 'g'):
		
		url = 'https://secure.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url = url,hash = hash,size = size,default = default,rating = rating)


	def generate_confirmation_token(self,expiration = 3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id}).decode('utf-8')

	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False

		if data.get('confirm') != self.id:
			return False

		self.confirmed = True
		db.session.add(self)
		db.session.commit()#confirmed提交到数据库
		return True
	
	@property
	def password(self):
		raise AttributeError('密码不给看')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	#刷新用户最后访问时间
	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)


	#生成虚拟用户供测试
	@staticmethod
	def generate_fake(count = 100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email = forgery_py.internet.email_address(),username = forgery_py.internet.user_name(True),password = forgery_py.lorem_ipsum.word(),confirmed = True,name = forgery_py.name.full_name(),location = forgery_py.address.city(),about_me = forgery_py.lorem_ipsum.sentence(),member_since = forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()



	def __repr__(self):
		return self.username


#未登录匿名用户
class AnonymousUser(AnonymousUserMixin):
	def can(self):
		return False

	def is_administrator(self):
		return False

loginmanager.anonymous_user = AnonymousUser



class PostCategory(db.Model):
	__tablename__ = 'postcategorys'
	id = db.Column(db.Integer,primary_key = True)
	name = db.Column(db.String(64),index = True,unique = True)
	posts = db.relationship('Post',backref = 'postcategory',lazy = 'dynamic')


class Comment(db.Model):
	__tablename__ = "comments"
	id = db.Column(db.Integer,primary_key = True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,index = True,default = datetime.utcnow)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))

	post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
		target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format = 'html'),tags = allowed_tags,strip = True))

#监听如果body变动，自动被调用	
db.event.listen(Comment.body,'set',Comment.on_changed_body)




class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer,primary_key = True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,index = True,default = datetime.utcnow)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	postcategory_id = db.Column(db.Integer,db.ForeignKey('postcategorys.id'))
	comments = db.relationship('Comment',backref = 'post',lazy = 'dynamic')

	#生成虚拟博客供测试
	@staticmethod
	def generate_fake(count = 100):
		from random import seed,randint
		import forgery_py

		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0,user_count-1)).first()
			p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),timestamp = forgery_py.date.date(True),author = u)
			db.session.add(p)
			db.session.commit()


#回调函数
@loginmanager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))





