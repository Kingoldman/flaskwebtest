
from .__init__ import mail
from flask_mail import Message
from threading import Thread
from flask import current_app,render_template


def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)


def send_mail(to,subject,template,**kwargs):

	msg = Message(subject = subject,sender = current_app.config['MAIL_DEFAULT_SENDER'],recipients = [to])
	msg.body = render_template(template + '.txt',**kwargs)
	msg.html = render_template(template + '.html',**kwargs)
	
	#线程要_get_current_object()
	thr = Thread(target = send_async_email,args = (current_app._get_current_object() ,msg))
	thr.start()
	return '<h1>邮件发送成功</h1>'
