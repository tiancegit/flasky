#!coding:utf-8
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer    # 使用itsdangerous生成令牌
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import login_manager

'''
数据库模型
'''



class Role(db.Model):   # 定义数据库模型
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # 只有一个角色的default字段要设为True，其他的都设为False。用户注册是其角色会被设为默认角色。
    permissions = db.Column(db.Integer)   # 添加了这个字段，其值是一个整数，表示位标志。各操作都对应一个位位置。能执行某项操作的角色。其位会被设为1
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

'''
下表列出了要支持的用户角色，以及定义角色使用的权限位。
表 用户角色

用户角色      权限               说明
匿名     0b00000000（0X00）    未登录的用户，在程序中只有阅读的权限。
用户     0b00000111（0X07）    拒用发布文章，发表评论和关注其他用户的权限。这是新用户的默认角色。
协管员   0b00001111（0X0f)     增加审查不当言论的权限。
管理员   0b11111111（0Xff）    具有所有权限，包括修改其他用户所属角色的权限。

使用权限组织角色，以后添加新角色只需使用不同的权限组合即可。

将角色手动添加到数据库既耗时也容易出错。作为替代。可以添加一个类，完成这个操作。
'''

    @staticmethod
    def insert_roles():
        roles = {
            'User' : (Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES, True),
            'Moderator' : (Permission.FOLLOW |
                           Permission.COMMENT |
                           Permission.WRITE_ARTICLES |
                           Permission.MODERATE_COMMENTS, False),
            'Administrator' : (0Xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default




'''
程序的权限
操  作                   位  值            说  明
关注用户              0b00000001(0x01)  关注其他用户
在他人的文章中发表评论  0b00000010(0x02)  在他人撰写的文章中发布评论
写文章                0b00000100(0x04)  写原创文章
管理他人发表的评论     0b00001000(0x08    查处他人发表的不当评论
管理员权限            0b10000000(0x80)   管理网站
表中的权限使用8位表示，现在只用了其中5位。其他3位可用于将来的补充。
表中的权限可以使用下面的代码表示。
'''


class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    # 添加了Email字段， 在这个程序中，用户使用电子邮件地址登陆，因为相对用户名而言，用户更不容易忘记自己的电子邮件地址。

    '''使用 Werkzeug 实现密码散列
    Werkzeug 中的 security 模块能够很方便地实现密码散列值的计算。这一功能的实现只需要
    两个函数,分别用在注册用户和验证用户阶段。
    • generate_password_hash(password, method= pbkdf2:sha1 , salt_length=8) :这个函数将
    原始密码作为输入,以字符串形式输出密码的散列值,输出的值可保存在用户数据库中。
    method 和 salt_length 的默认值就能满足大多数需求。
    • check_password_hash(hash, password) :这个函数的参数是从数据库'''

    '''计算密码散列值的函数通过名为 password 的只写属性实现。设定这个属性的值时,赋值
    方 法 会 调 用 Werkzeug 提 供 的 generate_password_hash() 函 数, 并 把 得 到 的 结 果 赋 值 给
    password_hash 字段。如果试图读取 password 属性的值,则会返回错误,原因很明显,因
    为生成散列值后就无法还原成原来的密码了。
    verify_password 方 法 接 受 一 个 参 数( 即 密 码 )
    , 将 其 传 给 Werkzeug 提 供 的 check_ password_hash() 函数,和存储在 User
    模型中的密码散列值进行比对。如果这个方法返回True ,就表明密码是正确的。'''

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

    '''
    dumps() 方法为指定的数据生成一个加密签名,然后再对数据和签名进行序列化,生成令
    牌字符串。  expiration 参数设置令牌的过期时间,单位为秒。
    generate_confirmation_token() 方法生成一个令牌,有效期默认为一小时。 confirm() 方
    法检验令牌,如果检验通过,则把新添加的 confirmed 属性设为 True 。
    '''

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    '''
    除了检验令牌, confirm() 方法还检查令牌中的 id 是否和存储在 current_user 中的已登录
    用户匹配。如此一来,即使恶意用户知道如何生成签名令牌,也无法确认别人的账户。
    '''

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    # expiration 令牌的过期时间

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

# 这段代码作用未明确


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))