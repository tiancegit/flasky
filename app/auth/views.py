#!coding:utf-8
from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_required, login_user
from ..models import User
from .forms import LoginForm


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






@auth.route('/secret')
@login_required     # login提供了一个装饰器，如果未认证用户访问路由，Flask-Login就会拦截请求，把用户发往登录页面
def secret():
    return 'Only authenticated users are allowed!'
