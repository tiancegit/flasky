#!coding:utf-8
# hello.py``
import os    # 导入os模块,数据库路径需要用到
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Manager, Shell
from datetime import datetime
from flask_wtf import FlaskForm   # 导入表单模块
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

from threading import Thread


manager = Manager(app)
moment = Moment(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class NameForm(FlaskForm):  # 定义表单
    name = StringField('what is your name?', validators=[Required()])
    submit = SubmitField('Submit')


def make_shell_context():                                #函数注册了程序,数据库实例,以及模型,因此这些对象可以导入到Shell
    return dict(app=app, db=db, User=User, Role=Role)    #为shell命令注册一个make_context回调函数,
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

# @app.route('/')       # 使用的app.route修饰器，把修饰的函数注册成路由
# def index():          # index注册成根路由的处理程序，这个函数的返回值叫做响应。
#     L='<h1>hello</h1>'
#     return render_template('index.html', L=L)  #reder_template 函数 第一个参数：模板的文件名 随后的参数为键值对。




@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_ADMIN']:
                send_mail(app.config['FLASK_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))

@app.route('/user/<name>')    #动态路由　name参数动态生成响应
def user(name):
    return render_template('user.html', name=name)   #name=name是关键字参数， 左边的name表示为参数名，就是模板中的占位符
                                                     #右边的name是当前作用域的变量，表示为同名参数的值。
                                                     #在模板中使用的{{ name }} 是一种特殊的占位符，告诉模板引擎在这个位置的值从渲染模时的数据获取。

#print app.url_map  可以用这个方法查看URL映射，其中的‘HEAD’, 'OPTIONS', 'GET'是请求方法，Flask指定了请求方法。HEAD和OPTIONS是Flask自动处理的。





if __name__ == '__main__':   #__name__ == __main__ 是python的惯常用法，直接启动脚本才会启动开发服务器，从其它脚本引入这个hello.py,就不会执行app.run
#    app.run(debug=True)      #程序实例使用run方法启动flask集成的Web开发的服务器,要是想启动调试模式，可以吧debug参数设为True.
    manager.run()