from flask import render_template,url_for,redirect,flash,request,abort,flash,current_app
from . import main
from ..models import User,Post,Comment
from flask_login import login_required,current_user
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,PostEditForm,CommentForm,DeleteCommentForm,DeletePostForm,PostEditForm
from ..__init__ import db,flask_whooshalchemyplus
from ..decorators import admin_required
import datetime


@main.route('/about',methods = ['POST','GET'])
def about():
	return render_template('about.html')

#资料页面路由
@main.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		abort(404)
	page = request.args.get('page',1,type = int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page,per_page = current_app.config['WHY_POSTS_PER_PAGE'],error_out = False)
	posts = pagination.items

	return render_template('user.html',user = user,posts = posts,pagination = pagination)

#用户级别编辑
@main.route('/edit_profile',methods = ['POST','GET'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash("你的个人资料已更新")
		return redirect(url_for('main.user',username = current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me

	return render_template('edit_profile.html',form = form)


#管理员级别编辑
@main.route('/edit_profile/<int:id>',methods = ['POST','GET'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user = user)
	if form.validate_on_submit():
		user.username = form.username.data
		user.email = form.email.data
		user.confirmed = form.confirmed.data
		user.is_administrator = form.is_administrator.data
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash("资料已更新")
		return redirect(url_for('main.user',username = user.username))

	form.username.data= user.username 
	form.email.data = user.email
	form.confirmed.data = user.confirmed
	form.is_administrator.data = user.is_administrator
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me

	return render_template('edit_profile.html',form = form)



@main.route('/',methods = ['POST','GET'])
@main.route('/index',methods = ['POST','GET'])
def index():
	form = PostForm()
	if form.validate_on_submit():
		#数据库需要真正的用户对象_get_current_object()
		post = Post( body = form.body.data,author = current_user._get_current_object())
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('main.index'))

	page = request.args.get('page',1,type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page = current_app.config['WHY_POSTS_PER_PAGE'],error_out = False)
	posts = pagination.items

	return render_template('index.html',title = '首页',form = form,posts = posts,pagination = pagination)


@main.route('/post/<int:id>',methods = ['GET','POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		if current_user.is_authenticated:
			comment = Comment(body = form.body.data,post = post,author = current_user._get_current_object())
			db.session.add(comment)
			db.session.commit()
			flash("评论成功！")
		else:
			flash("登录之后才能评论！")
		return redirect(url_for('main.post',id = post.id))
		
	page = request.args.get('page',1,type = int)
	if page == -1:
		page = (post.comments.count() - 1) / current_app.config['WHY_COMMENTS_PER_PAGE'] + 1

	pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,per_page = current_app.config['WHY_COMMENTS_PER_PAGE'],error_out = False )
	comments = pagination.items
	#接收列表，为了_posts.html使用
	return render_template('post.html',posts = [post],form = form,comments = comments,pagination = pagination)

@main.route('/deletecomment/<int:id>',methods = ['GET','POST'])
@login_required
def deletecomment(id):
	comment = Comment.query.get_or_404(id)
	if current_user != comment.author and not current_user.can():
		abort(403)
	post = Post.query.get_or_404(comment.post.id)
	form = DeleteCommentForm()
	if form.validate_on_submit():
		if comment and post:
			db.session.delete(comment)
			db.session.commit()
			flash("评论删除成功")
			return redirect(url_for('main.allonepost',id = post.id))

	return render_template('deletecomment.html',form = form,comments = [comment])
	



@main.route('/edit/<int:id>',methods = ['GET','POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can():
		abort(403)
	form = PostEditForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		db.session.commit()
		flash("文章内容已更新")
		return redirect(url_for('main.allonepost',id = post.id))

	form.body.data  = post.body 
	return render_template('edit_post.html',form = form)


@main.route('/deletepost/<int:id>',methods = ['GET','POST'])
@login_required
def deletepost(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can():
		abort(403)
	comments = Comment.query.filter_by(post_id = id).all()
	form = DeletePostForm()
	if form.validate_on_submit():
		if comments:
			for comment in comments:
				db.session.delete(comment)
			db.session.commit()
			flash("文章评论删除成功")
		if post:
			db.session.delete(post)
			db.session.commit()
			flash("文章删除成功")
			return redirect(url_for('main.index'))

	return render_template('delete_post.html',form = form,post = post)




@main.route('/allonepost/<int:id>',methods = ['GET','POST'])
def allonepost(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		if current_user.is_authenticated:
			comment = Comment(body = form.body.data,post = post,author = current_user._get_current_object())
			db.session.add(comment)
			db.session.commit()
			flash("评论成功！")
		else:
			flash("登录之后才能评论！")
		return redirect(url_for('main.allonepost',id = post.id))
	
	#评论分页
	page = request.args.get('page',1,type = int)
	if page == -1:
		page = (post.comments.count() - 1) / current_app.config['WHY_COMMENTS_PER_PAGE'] + 1

	pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,per_page = current_app.config['WHY_COMMENTS_PER_PAGE'],error_out = False )
	comments = pagination.items
	#接收列表，为了_posts.html使用
	return render_template('onepost.html',post = post,form = form,comments = comments,pagination = pagination)

@main.route('/follow/<username>',methods = ['GET','POST'])
@login_required
def follow(username):
	user = User.query.filter_by(username = username ).first()
	if user is None:
		flash("错误！")
		return redirect(url_for('main.index'))
	if current_user.is_following(user):
		flash("你已经关注了%s"%username)
		return redirect(url_for('main.user',username = username))
	current_user.follow(user)
	flash("你关注了%s"%username)
	return redirect(url_for('main.user',username = username))


@main.route('/unfollow/<username>',methods = ['GET','POST'])
@login_required
def unfollow(username):
	user = User.query.filter_by(username = username ).first()
	if user is None:
		flash("错误！")
		return redirect(url_for('main.index'))
	if not current_user.is_following(user):
		flash("你没有关注%s"%username)
		return redirect(url_for('main.user',username = username))
	current_user.unfollow(user)
	flash("你取消了关注%s"%username)
	return redirect(url_for('main.user',username = username))

@main.route('/followers/<username>',methods = ['GET','POST'])
@login_required
def followers(username):
	user = User.query.filter_by(username = username ).first()
	if current_user != user and not current_user.can():
		abort(403)
	if user is None:
		flash("错误！")
		return redirect(url_for('main.index'))
	page = request.args.get('page',1,type = int)
	pagination = user.followers.paginate(page,per_page = current_app.config['WHY_FOLLOWERS_PER_PAGE'],error_out = False)
	follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',user = user,endpoint = 'main.followers',pagination = pagination,follows = follows)



@main.route('/followed_by/<username>',methods = ['GET','POST'])
@login_required
def followed_by(username):
	user = User.query.filter_by(username = username ).first()
	if current_user != user and not current_user.can():
		abort(403)
	if user is None:
		flash("错误！")
		return redirect(url_for('main.index'))
	page = request.args.get('page',1,type = int)
	pagination = user.followed.paginate(page,per_page = current_app.config['WHY_FOLLOWERS_PER_PAGE'],error_out = False)
	follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followed_by.html',user = user,endpoint = 'main.followed_by',pagination = pagination,follows = follows)



@main.route('/myfollow',methods = ['GET','POST'])
@login_required
def myfollow():
	posts = current_user.followed_posts

	page = request.args.get('page',1,type = int)
	pagination = posts.paginate(page,per_page = current_app.config['WHY_POSTS_PER_PAGE'],error_out = False)
	posts = pagination.items

	return render_template('index.html',posts = posts,title = '我的关注',pagination = pagination)


@main.route('/search',methods = ['GET','POST'])
@login_required
def search():
	if not request.form['search']:
		return redirect(url_for('main.index'))
	return redirect(url_for('main.sh_results',keywords = request.form['search']))

@main.route('/sh_results/<keywords>')
@login_required
def sh_results(keywords):

	flask_whooshalchemyplus.index_one_model(Post)
	results = Post.query.whoosh_search(keywords)

	page = request.args.get('page',1,type = int)
	pagination = results.paginate(page,per_page = current_app.config['WHY_POSTS_PER_PAGE'],error_out = False)
	posts = pagination.items

	return render_template('sh_results.html',keywords = keywords,posts = posts,pagination = pagination)


