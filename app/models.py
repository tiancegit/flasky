#!coding:utf-8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
'''
数据库模型
'''

'''使用 Werkzeug 实现密码散列
Werkzeug 中的 security 模块能够很方便地实现密码散列值的计算。这一功能的实现只需要
两个函数,分别用在注册用户和验证用户阶段。
• generate_password_hash(password, method= pbkdf2:sha1 , salt_length=8) :这个函数将
原始密码作为输入,以字符串形式输出密码的散列值,输出的值可保存在用户数据库中。
method 和 salt_length 的默认值就能满足大多数需求。
• check_password_hash(hash, password) :这个函数的参数是从数据库'''


class Role(db.Model):   # 定义数据库模型
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

# 添加了Emai字段， 在这个程序中，用户使用电子邮件地址登陆，因为相对用户名而言，用户更不容易忘记自己的电子邮件地址。

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    # 加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户,这个函数必须返回用户对象;否则应该返回 None 。
    def load_user(user_id):
        return User.query.get(int(user_id))


'''计算密码散列值的函数通过名为 password 的只写属性实现。设定这个属性的值时,赋值
方 法 会 调 用 Werkzeug 提 供 的 generate_password_hash() 函 数, 并 把 得 到 的 结 果 赋 值 给
password_hash 字段。如果试图读取 password 属性的值,则会返回错误,原因很明显,因
为生成散列值后就无法还原成原来的密码了。
verify_password 方 法 接 受 一 个 参 数( 即 密 码 )
, 将 其 传 给 Werkzeug 提 供 的 check_
password_hash() 函数,和存储在 User 模型中的密码散列值进行比对。如果这个方法返回
True ,就表明密码是正确的。'''

