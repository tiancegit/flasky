#!coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, length, Email
'''
电子邮件字段用到了 WTForms 提供的 Length() 和 Email() 验证函数。 PasswordField 类表
示属性为 type="password" 的 <input> 元素。 BooleanField 类表示复选框。

'''

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me Logged in')
    submit = SubmitField('Log In')
