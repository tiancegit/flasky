#!coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, length, Email, Regexp, EqualTo

from ..models import User

'''
电子邮件字段用到了 WTForms 提供的 Length() 和 Email() 验证函数。 PasswordField 类表
示属性为 type="password" 的 <input> 元素。 BooleanField 类表示复选框。
'''

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me Logged in')
    submit = SubmitField('Log In')


'''
注册页面使用的表单要求用户输入电子邮件地址，用户名，密码，这个表单如下所示。
'''


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[Required(), length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                     'Usernames must have only letters,'
                                                                                     'numbers,dots or Underscores')])
    # 这里使用了WTForms提供的Regexp验证函数，确保username字段只包含了字母数字下划线和点号，这个验证函数中正则表达式后面的两个参数分别是
    # 正则表达式的旗标和验证失败是显示的错误信息。

    # 安全起见，密码要输入两次，此时要验证两个密码字段的值是否一致，这种验证可使用WTForms的一个验证函数实现，即 Equalto 。
    # 这个验证函数要附属到两个密码字段中的一个上，另一个要作为参数传入。

    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    # 这个表单中还有两个自定义的验证函数，以方法的形式实现，如果表单类中定义了validate_开头，且跟着字段名的方法，这个方法就和
    # 常规的验证函数一起调用，这里分别为email和username字段定义了验证函数，确保填写的值没有在数据库中出现过，自定义的验证函数
    # 想要表示验证失败，可以抛出ValidationError异常，其参数就是错误信息。

    # 现在表单层面处理好邮件和用户名重复的问题，数据没问题了再交给视图函数处理。



    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in user.')

    # 显示这个表单的模板是/templates/auth/register.html，和登录模板一样，这个模板也使用wtf.quick_form()渲染表单。


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')


# 提交重设密码要求时,提交要重设密码的邮箱用户的表单.

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(), length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField("Email", validators=[Required(), length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Password must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

# 一个错误处理函数,查询邮箱是否存在于数据库中,若否,则返回一个错误信息.

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unkown Email address.')

# 提交 修改邮件申请 页面的表单。


class ChangeEmailForm(FlaskForm):
    email = StringField("New Email", validators=[Required(), length(1, 64), Email()])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():    # 若数据库中存在邮箱地址，则返回一个邮箱已经被注册的信息
            raise ValidationError('Email already registered.')











