
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,SubmitField,PasswordField,TextAreaField,SelectField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from app.models import User,Comment,Post
from flask_pagedown.fields import PageDownField


#用户资料管理
class EditProfileForm(FlaskForm):
	name = StringField('真实姓名',validators = [Length(0,64)],render_kw={"placeholder": "请输入你的姓名（可选）"})
	location = StringField('地址',validators = [Length(0,64)],render_kw={"placeholder": "请输入你的位置（可选）"})
	about_me = TextAreaField('个人说明',render_kw={"placeholder": "请输入你的个人说明（可选）"})
	submit = SubmitField('保存')


#管理员权限资料编辑
class EditProfileAdminForm(FlaskForm):
	username = StringField('用户名',validators = [DataRequired(),Length(1,64)],render_kw={"placeholder": "请输入用户名"})
	email = StringField('Email',validators = [DataRequired(),Email(message="邮箱格式错误"),Length(1,64)],render_kw={"placeholder": "yourname@example.com"})

	confirmed = BooleanField("是否激活")
	is_administrator = BooleanField("是否管理员")

	name = StringField('真实姓名',validators = [Length(0,64)],render_kw={"placeholder": "请输入姓名（可选）"})
	location = StringField('地址',validators = [Length(0,64)],render_kw={"placeholder": "请输入位置（可选）"})
	about_me = TextAreaField('个人说明',render_kw={"placeholder": "请输入个人说明（可选）"})
	submit = SubmitField('保存')

	def __init__(self,user,*args,**kwargs):
		super(EditProfileAdminForm,self).__init__(*args,**kwargs)
		self.user = user


	def validate_email(self,email):
		#验证是否有变化，无变化则略过,有变化但是不能喝数据库其他重复
		if email.data != self.user.email and User.query.filter_by(email = email.data).first():
			raise ValidationError("邮箱已注册")

	def validate_username(self,username):
		if username.data != self.user.username and User.query.filter_by(email = username.data).first():
			raise ValidationError("用户名已注册")
'''
#markdown文章表单
class PostForm(FlaskForm):
	#title = StringField("标题",validators = [DataRequired(),Length(1,64)],render_kw={"placeholder": "这里填写文章标题"})
	body = PageDownField("内容",validators = [DataRequired()],render_kw={"placeholder": "这里填写文章内容，支持MarkDown语法"})
	#postcategory = SelectField( label='文章类别',validators=[DataRequired('请选择文章类别')],coerce=int)
	submit  = SubmitField("发表")
'''


class PostForm(FlaskForm):
	body = TextAreaField("内容",validators = [DataRequired()])
	submit  = SubmitField("发表")


class PostEditForm(FlaskForm):
	body = TextAreaField("内容",validators = [DataRequired()])
	submit  = SubmitField("提交")


class CommentForm(FlaskForm):
	body = PageDownField("内容",validators = [DataRequired()],render_kw={"placeholder": "这里填写评论内容，支持MarkDown语法"})
	submit  = SubmitField("发表")

class DeleteCommentForm(FlaskForm):
	submit  = SubmitField("点击删除评论")

class DeletePostForm(FlaskForm):
	submit  = SubmitField("点击删除文章")