
from flask_wtf import FlaskForm

from wtforms import StringField,BooleanField,SubmitField,PasswordField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from app.models import User


class LoginForm(FlaskForm):
	email = StringField('Email',validators = [DataRequired(),Email(message="邮箱格式错误")],render_kw={"placeholder": "yourname@example.com"})
	password = PasswordField('密码',validators = [DataRequired(),Length(8,16)],render_kw={"placeholder": "请输入8-16位密码"})
	verification_code =  StringField('验证码',validators = [DataRequired()],render_kw={"placeholder": "请输入验证码"})
	remember_me = BooleanField('记住我')
	submit = SubmitField('登陆')

class RegistrationForm(FlaskForm):
	username = StringField('用户名',validators = [DataRequired(),Length(1,64)],render_kw={"placeholder": "请输入用户名"})
	email = StringField('Email',validators = [DataRequired(),Email(message="邮箱格式错误"),Length(1,64)],render_kw={"placeholder": "yourname@example.com"})
	password = PasswordField('密码',validators = [DataRequired(),EqualTo('password2',message = "密码不一致"),Length(8,16)],render_kw={"placeholder": "请输入8-16位密码"})
	password2 = PasswordField('重复密码',validators = [DataRequired(),Length(8,16)],render_kw={"placeholder": "请再输入一遍密码"})
	verification_code =  StringField('验证码',validators = [DataRequired()],render_kw={"placeholder": "请输入验证码"})
	submit = SubmitField('注册')

	def validate_username(self,username):
		user = User.query.filter_by(username = username.data).first()
		if user is not None:
			raise ValidationError("用户名已注册")

	def validate_email(self,email):
		user = User.query.filter_by(email = email.data).first()
		if user is not None:
			raise ValidationError("邮箱已注册")


class ChangePasswordForm(FlaskForm):
	oldpassword = PasswordField('原密码',validators = [DataRequired()],render_kw={"placeholder": "请输入你的原密码"})
	newpassword = PasswordField('新的密码',validators = [DataRequired(),EqualTo('newpassword2',message = "密码不一致"),Length(8,16)],render_kw={"placeholder": "请输入你新的密码"})
	newpassword2 =PasswordField('再输入一遍',validators = [DataRequired(),Length(8,16)],render_kw={"placeholder": "请确认你新的密码"})

	submit = SubmitField('确认修改')