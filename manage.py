#!coding:utf-8
import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv("FLASK_CONFIG") or 'default')   #从环境变量中获取配置，若环境变量没有，则采用默认配置
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():                                # 函数注册了程序,数据库实例,以及模型,因此这些对象可以导入到Shell
    return dict(app=app, db=db, User=User, Role=Role)    # 为shell命令注册一个make_context回调函数,
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():

    '''Run the unit test'''

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
