#!coding:utf-8
from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_required, login_user, logout_user
from ..models import User, db
from .forms import LoginForm, RegistrationForm


''' 这个函数创建了一个LoginForm对象，当请求类型是Get的时候，视图直接渲染模板，既显示表单，当表单在POST请求中提交时，Flask-wtf中的
validate_on_submit()函数会验证表单数据，然后尝试登入用户。

为了登入用户，视图函数首先使用表单中填写的email从数据库中加载用户。如果电子邮件的对应用户存在，再调用用户对象的verify_password()
方法，其参数是表单中填写的密码，如果密码正确，则调用Flask-login中的Login_user()函数，在用户会话中把用户标记为已登录
login_user()函数的参数是要登录的用户，以及可选的 ‘记住我’ 布尔值，‘记住我’也要在表单中填写，如果值为False,那么关闭浏览器后，
用户会话则过期，所以下次用户访问时要重新登录，如果值为True，那么会在用户浏览器中写入一个长期有效的Cookie，使用这个cookie可以复现用户会话。

提交密令的POST请求最后也做了重定向，不过目标URL有两种可能，用户访问未授权的URL是会显示登录表单，Flask-Login会把原地址保存在查询字符串的Next
参数，这个参数可以从request.args字典中读取。如果查询字符串中没有next参数，则重定向发到首页，如果用户输入的电子邮件或者密码不正确，程序会设定一个Flash消息，
再次渲染表单，让用户重试登录
'''


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)



'''~~ 在生产服务器上，登录路由必须使用安全的HTTP。从而加密传送给服务器的表单数据，如果没有使用安全的Http，登录密令在传输的过程中可能会被截取，在服务器上花再多的
的精力来保证密码安全都是无济于事。'''

'''为了登出用户，这个视图函数调用Flask_login中的logout_user()函数，删除并重设了会话，随后会显示一个flash信息，确认这次操作，
再重定向到首页，这样登出就完成了。'''


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

'''提交注册表单后，通过验证后，系统就使用用户填写的信息在数据库中注册一个新用户，处理这个任务的视图函数如下'''


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash("You can now login")
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)


@auth.route('/secret')
@login_required     # login提供了一个装饰器，如果未认证用户访问路由，Flask-Login就会拦截请求，把用户发往登录页面
def secret():
    return 'Only authenticated users are allowed!'