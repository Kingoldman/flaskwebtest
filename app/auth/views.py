
from flask import render_template,url_for,redirect,flash,request,session,make_response
from . import auth
from .forms import LoginForm,RegistrationForm,ChangePasswordForm
from app.models import User
from flask_login import login_user,logout_user,login_required,current_user
from .. import db
from app.email import send_mail
from . import utils_en,verifycode_generator



#验证码
@auth.route('/verifycode',methods = ['POST','GET'])
def get_verify_code():
	#把strs发给前端,或者在后台使用session保存
    code_img, code_text = utils_en.generate_verification_code()
    session['code_text'] = code_text
    response = make_response(code_img)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@auth.route('/register',methods = ['POST','GET'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		if 'code_text' in session and session['code_text'] != form.verification_code.data:
			flash('验证码输入错误!')
		else:
			user = User(username = form.username.data,email = form.email.data,password = form.password.data)
			db.session.add(user)
			db.session.commit()
			token = user.generate_confirmation_token()
			send_mail(user.email,"激活账户",'auth/email/confirm',user = user,token = token)
			flash("一封激活邮件已经发送到你的邮箱，请激活")
			return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form = form)


@auth.route('/login',methods = ['POST','GET'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if 'code_text' in session and session['code_text'] != form.verification_code.data:
			flash('验证码输入错误!')
		else:
			user = User.query.filter_by(email = form.email.data).first()
			if user is not None and user.verify_password(form.password.data):
				login_user(user,form.remember_me.data)
				flash("登陆成功")
				next = request.args.get('next')
				if next is None or not next.startswith('/'):
					next = url_for('main.index')
				return redirect( next )
			else:
				flash('账户名或密码错误')
	return render_template('auth/login.html',form = form)


@auth.route('/logout',methods = ['POST','GET'])
@login_required
def logout():
	logout_user()
	flash("已经退出！")
	return redirect(url_for('main.index'))



@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		#db.session.commit()#如果只在这里提交添加不进去数据库？非要在confirm函数里去提交
		flash("激活成功！")
	else:
		flash("错误！")
	return redirect(url_for('main.index'))



@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		#更新登陆用户访问时间
		current_user.ping()
		if not current_user.confirmed and request.endpoint[:5] != 'auth.'and request.endpoint != 'static':

			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))

	return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_mail(current_user.email,'激活邮件','auth/email/confirm',user = current_user,token = token)
	flash("一封激活邮件已经发送到你的邮箱，请激活")
	return redirect(url_for('main.index'))



@auth.route('/change_password',methods = ['POST','GET'])
@login_required
def changepassword():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.oldpassword.data):
			current_user.password = form.newpassword.data
			#db.session.add(current_user)这里不需要，因为先login了进行了user = User.query.filter_by操作it's added to the session when you do the query.
			db.session.commit()
			flash("密码修改成功！")
			return redirect(url_for('main.index'))
		else:
			flash("原始密码错误！")
	return render_template('auth/changepassword.html',form = form)
