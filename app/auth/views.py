#!coding:utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from .forms import *
from ..email import send_email
from ..models import User, db

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

# 当前的 /register 路由把新用户添加到数据库中后,会重定向到 /index。在重定向之前,这个路由需要发送确认邮件。


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm You Account', 'auth/email/confirm', user=user, token=token,)
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

'''
Flask-login提供的login_required修饰器会保护这个路由,因此用户点击确认邮件的连接后,要先登录,然后才可以执行这个视图函数.

这个函数先检查已登录用户是否登录过,如果确认过,则重定向到首页,因为此时不用做什么操作,这样处理可以避免用户不小心点击确认令牌带来额外的工作.

由于令牌确认工作完全在User模型中完成,所以视图函数只需要调用confirm()方法即可,然后再根据确认结果的不同显示不同的flash信息,确认成功之后,
User模型中的confirmed的值会被修改并添加到会话中,请求处理完成后,这两个操作被提交到数据库.
'''


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

'''
每个程序都可以决定用户确认账户之前可以做些什么操作,比如允许未确认的用户登录,这个页面要求用户获取权限之前先确认账户.

这一步可以使用 Flask提供的before_request钩子完成,对于蓝本来说,before_request钩子只能应用到属于蓝本的请求上,若是想在蓝本中使用
针对程序全局请求的钩子,必须使用before_app_request修饰器,
'''


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')  # 只渲染一个模板,有如何确认账户的说明,此外还提供一个链接,用于发送新的确认邮件.

'''同时满足下面的三个条件before_app_request会拦截请求,1: 用户已登录(current_user.is_authenticated()必须返回True.  2: 用户的
账户还未确认. 3: 请求的端点(使用request.endpoint获取)不在认证蓝本中,访问认证路由要获取权限,因为这些路由的作用是让用户确认账户或者
执行其它账户操作的.   如果请求满足以上的三个条件,则会被重定向到 /auth/unconfirmed 路由, 显示一个相关信息的页面.'''

'''如果 before_request或before_app_request的回调函数返回相应或者重定向,Flask会直接将其发送到客户端,而不会调用请求的视图函数,因此这些
会在必要时拦截请求.'''

# 重新发送账户确认邮件.

'''这个路由为 current_user（既是已登录用户，也是目标用户）用户，重做了一遍注册路由中的操作，这个路由也用login_required保护，
确保访问时程序知道请求再次发送邮件的是那个用户。'''


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))

'''verify_password 方 法 接 受 一 个 参 数( 即 密 码 ), 将 其 传 给 Werkzeug 提 供 的 check_ password_hash()
 函数,和存储在 User 模型中的密码散列值进行比对。如果这个方法返回True ,就表明密码是正确的。
# 修改密码的路由，引入相对应的表，取Old_password 的值与数据库中值相比较，若返回True，则进行下一步！ 把新密码提交到数据库中。
flash一个信息，你的密码已经被更新，并重定向到首页，否则Flash一个无效密码信息。
'''


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:  # anonymous 无名的,匿名的
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
            'sent to you')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('You password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been update.')
    else:
        flash('Invalid request')
    return redirect(url_for('main.index'))



@auth.route('/secret')
@login_required     # login提供了一个装饰器，如果未认证用户访问路由，Flask-Login就会拦截请求，把用户发往登录页面
def secret():
    return 'Only authenticated users are allowed!'


