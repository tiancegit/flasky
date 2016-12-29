#!coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, length


class NameForm(FlaskForm):    # 定义表单
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# 普通用户的资料编辑表单/ 这个表单的所有字段都是可选的。


class EditProfileForm(FlaskForm):
    name = StringField("Real name", validators=[length(0, 64)])
    location = StringField('location', validators=[length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


# 管理员级别的资料管理器。

class EditProfileAdmin