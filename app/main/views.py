#!coding:utf-8
from flask import render_template, session, redirect, url_for, current_app, abort, flash
from flask_login import login_required, current_user

from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..decorators import admin_required, permission_required
from ..email import send_email
from ..models import User, Permission


@main.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASK_ADMIN']:
                send_email(current_app.config['FLASK_A'
                                              'DMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))


''' 为每个用户创建资料页面, 这个路由在main蓝本中添加,对于名为 john的用户,其资料页面的地址是 http://localhost:5000/user/john.
这个视图函数会在数据库中搜索 URL 指定的用户名,如果找到,则渲染模板user.html,并把用户名作为参数传入模板,如果传入路由的用户名不存在,则返回404错误.
user模板用过渲染保存在用户对象中的信息,这个模板的初始版本:app/templates/user.html
'''


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

# 用户编辑资料的路由

'''
在显示表单之前，视图函数给所有字段设定了初始值。对于给定的字段，这一个工作是通过初始值赋值给form.<field-name>.date完成的。
当form.validate_on_submit()返回False时，表单的三个字段都会使用current_user中保存的初始值。提交表单之后，表单字段的data属性中保存有
更新后的值，因此可以将其赋值给用户对象中的各字段，然后再把用户对象添加到数据库会话中。
为了方便用户能轻易找到编辑页面，可以在资料页面中添加一个链接。>>user.html
'''


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been update')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)



'''
@main.route('/user/<name>')    # 动态路由　name参数动态生成响应
def user(name):
    return render_template('user.html', name=name)   # name=name是关键字参数， 左边的name表示为参数名，就是模板中的占位符
                                                     # 右边的name是当前作用域的变量，表示为同名参数的值。
                                                     # 在模板中使用的{{ name }} 是一种特殊的占位符，告诉模板引擎在这个位置的值从渲染模时的数据获取。

# print app.url_map  可以用这个方法查看URL映射，其中的‘HEAD’, 'OPTIONS', 'GET'是请求方法，Flask指定了请求方法。HEAD和OPTIONS是Flask自动处理的。
'''

'''
这是演示 decorators 装饰器例子的两个页面

在模板中可能也需要检查权限,所以 Permission 类为所有位定义了变量.为了避免每次调用 render_template()时多添加一个参数,
可以使用上下文,上下文处理器能使变量在所有模板中全局可访问.
修改app/main/__init__.py: 把 Permission 类加入模板上下文.

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
'''

# 举两个例子用于使用自定义的修饰器。  权限判断修饰器。


@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return 'For administrators!'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For comment moderators!'
