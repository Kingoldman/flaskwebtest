from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Shell
from app import create_app,db
from app.models import *
import os
import flask_whooshalchemyplus

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app,db)


def make_shell_context():
	return dict(app = app ,db = db,User = User,Post = Post,Comment = Comment,Follow = Follow)

manager.add_command('shell',Shell(make_context = make_shell_context))
manager.add_command('db',MigrateCommand)

#索引
flask_whooshalchemyplus.whoosh_index(app,Post)


@manager.command
def deploy():
	from flask_migrate import upgrade
	upgrade()