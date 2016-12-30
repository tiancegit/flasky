#!coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class NameForm(FlaskForm):    # 定义表单
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# 普通用户的资料编辑表单/ 这个表单的所有字段都是可选的。


class EditProfileForm(FlaskForm):
    name = StringField("Real name", validators=[Length(0, 64)])
    location = StringField('location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


# 管理员级别的资料管理器。

'''WTForms对表单控件<select>进行了selectField包装，从而实现下拉列表，在表单中选择用户角色，SelectField实例必须在choices属性中设置各属性。
选项必须是一个由元祖组成的列表，各元祖都包含两个元素，选项的标识符和显示在控件中的文本字符串。choices列表在表单的构造函数中设定，其值从Role
模型中获取，使用一个查询角色名的字母顺序排列所有角色。元祖的标识符是角色的id，因为这是个整数，所以在SelectField构造函数中添加coerce=int
参数，从而把字段的值转换成整数，而不使用默认的字符串。

email 和username字段的构造方式和认证表单中的一样，但处理验证的时候需要更小心。验证这两个字段的时候，首先要先检查字段的值是否发生了变化，如果有变化，
就要保证新值不和其它用户的相应字段值重复。如果字段值没有变化，则应该跳过验证，为了实现这个逻辑，表单的构造函数接收用户对象作为参数，并将其保存在
成员变量中，随后自定义的验证方法要使用这个用户对象。'''

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(),
                                                   Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                         'Usernames must have only letters, '
                                                                         'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Role name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')
