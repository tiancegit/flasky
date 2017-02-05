#!coding:utf-8
import hashlib
from datetime import datetime

import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer    # 使用itsdangerous生成令牌
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import login_manager

'''
数据库模型
'''

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


# 这是关联表


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


class Role(db.Model):   # 定义数据库模型
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # 只有一个角色的default字段要设为True，其他的都设为False。用户注册是其角色会被设为默认角色。
    permissions = db.Column(db.Integer)   # 添加了这个字段，其值是一个整数，表示位标志。各操作都对应一个位位置。能执行某项操作的角色。其位会被设为1
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        ''' 函数并不直接创建新角色对象,而是通过角色名查找现有的角色,然后再进行更新,只用当数据库
        没有某个角色名才会去创建新角色对象,如此一来,如果以后更新了角色列表,就可以执行更新操作了,如果
         想添加新角色或者修改角色的权限,修改rolse数组,再运行函数即可, 匿名角色不需要在数据库中表示出来,这个角色的作用
         是为了表示不在数据库中的用户.'''
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    # 用户信息字段
    # 新加的字段保存了用户的真实名字,所在地,自我介绍,注册日期和最后访问日期.
    # abour_me 字段的类型是 db.Text(),db.String和db,Text的区别在于后者不需要指定最大长度.
    # 两个时间戳的默认值是当前时间,注意 datetime.utcnow后面没有(),因为db.Column()的 default参数可以接受函数作为默认值.
    # 所以每次需要生成默认值时,db.Column()都会调用指定的函数,member_since字段只需要默认值即可.
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    avatar_hash = db.Column(db.String(32))   # 生成头像时生成MD5值，计算量会非常大，由于用户的邮件地址的MD5值是不变的。可以保存在数据库中。
    posts = db.relationship("Post", backref="author", lazy="dynamic")  # 这是和Post模型之间的一对多关系。
    # User模型与comments表的一对多关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    # last_seen字段创建时的初始值也是当前时间,但用户每次访问网站后,这个值都会被刷新,在user模型添加一个方法去完成这个操作.

    # 多对多关系分拆出来的两个基本一对多关系.而且要定义成标准关系.
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # 这段代码中,followed和followers关系都定义为单独的一对多关系.注意了,为了消除外键间的歧义,定义关系时必须使用可选参数foreign_keys
    # 指定的外键.而且,db.backref()参数并不是指定这两个参数之间的引用关系.而是回引 Follow 模型. 回引中的lazy参数指定为joined.这个lazy
    # 模式可以实现从联结查询中加载相关对象,例如,某个用户关注了100个用户,调用user.followed.all()后会返回一个列表.其中包含100个follow
    # 实例,每一个实例的follower 和 followed回引属性都指向相应的用户,设定为lazy='joined'模式,就可以在一次数据库查询中完成这些操作.
    # 如果,lazy的设为select,那么首次访问follower 和 followed 属性时才会加载对应的用户,而且每个属性都需要单独的一个查询.这就意味着获取
    # 全部被关注的用户时需要增加100次额外的数据库查询.

    '''
    这两个关系中,User一侧设定的lazy参数作用不一样,lazy参数都在'一'这一侧设定,返回的是'多'的这一侧中的记录.上述代码使用的是 dynamic.
    因此关系属性不会直接返回记录,而是返回查询对象.所以在执行查询之前还可以添加额外的过滤器.
    '''

    '''
    cascade 参数配置在父对象上执行的操作对相关对象的影响.比如,层叠选项可设为:将用户添加到数据库会话后,要自动把所有关系的对象添加到会话中,
    层叠选项的默认值能满足大多数情况下的需求.但对这个多对多关来说却不合用.删除对象时,默认的层叠行为是把所有相关对象的外键设为空值.但在
    关联表中.删除记录后的正确行为应该是把指向该实体也删除.因为这样能有效销毁链接,这就是层叠选项值delete-orphan的作用.

    cascade 参数的值是一组由逗号分隔的分隔的层叠选项,这看起来可能让人有点困惑,但 all 表示除了delete-orphan 之外的层叠选项,设为all.
    delete-orphan的意思是启用所有的默认层叠选项,而且还要删除孤儿选项.
    '''
# 定义一个刷新用户最后访问时间。

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

        # 每次收到用户的请求时都调用ping()方法,由于 auth蓝本中的before_app_request处理程序在每次请求前运行,所以能轻松实现这个需求
        # 跳转到 app/auth/views.py

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
        # 更新了电子邮件地址，则重新计算散列值。
        self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()

        db.session.add(self)
        return True

    # Uesr类的构造函数首先调用基类的构造函数,如果创建基类对象后还没定义角色,
    # 则根据电子邮件地址决定将其设为管理员或者默认角色

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # 模型初始化的过程中会计算电子邮件的散列值，然后存入数据库。
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)  # 注册时把用户设为自己的关注者.  但数据库中已经创建了一些用户,而且没有关注自己,可以添加一个函数,更新现有用户.
    # 为了简化角色和权限的实现过程,可在User模型中添加一个辅助方法,检查是否有指定的权限.
    # 检查用户是否有指定的权限.

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions
    # 方法在请求和赋予角色这两种权限之间进行位与操作,如果角色中包含请求的所有权限位,则返回True,
    # 表示允许用户执行此项操作,

    # 检查管理员权限的功能经常用到,因此使用了单独的is_administrator()方法实现.
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username

    '''Gravatar查询字符串参数。
    参数名     说明
     s      图片大小。单位为像素
     r      图片级别。可选值有"g". "pg". 'r'和"x"
     d      没有注册gravatar服务的用户使用默认的图片生成方式，可选值有："404"，返回404错误。默认的图片的
            URL;图片生成器"mm","identicon","monsterid", "wavatar", "retro" 或 "blank"之一
     fd     强制使用默认头像
     可以构建Gravatar URL的方法添加到User模型中，
    '''

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravtar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        # 如果模型中没有，就和之前一样计算电子邮件地址的散列值。
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    '''这一实现会选择标准或者加密的gravatar URL基以匹配用户的安全需求，头像的URL有URL基，用户电子邮件地址的MD5散列值和各参数组成。
    而各参数都设定了默认值。有上述实现，可以在python shell中轻易生成头像的URL了'''

    '''
    程序现在要处理两个一对多关系,以便实现多对多关系.由于这些操作经常需要重复执行,最好在user模型中为所有可能的操作定义辅助方法.用于控制关注关系
    的四个方法.
    '''

    # Follow方法手动把follow方法实例插入关联表.从而把关联者和被关联者连接起来.并让程序有机会设定自定义字段的值.联接在一起的两个用户被手动
    # 传入follow类的构造器.创建一个Follow新实例.然后像往常一样.把这个实例对象添加到数据库会话中.注意,这里无需手动设定timestamp字段.
    # 因为定义字段的时指定了默认值,即是当前日期和时间.
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    # unfollow()方法使用了follow关系找到了联接用户和被关注的用户的follow实例.若要销毁这两个用户之间的联接.只需要删除这个follow对象即可.

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    # is_following()方法和is_followed_by()方法,分别在左右两边的一对多关系中搜索指定用户.如果找到了就返回True.

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    # 定义一个联结查询,用于让用户选择查看关注用户发布的博客文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    # flowed_posts() 方法定义为属性.因此调用时无需加().如此一来.所有关系的句法都是一样了.

    # 添加到User的类方法，用于生成虚拟数据。P119

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        # 用户的邮箱地址，和用户名必须是唯一的，但forgeryPy随机生成信息，用重复的风险，虽然出现的几率很小，提交数据库时会抛出异常。
        # 处理方式是，在继续操作之前回滚会话，在循环中生成重复内容时不把用户写入数据库。因此生成的虚拟用户总数可能会比预期的少。

    """这个函数用于自动更新数据库中已有的数据,把用户自己关注自己的账号.创建函数更新数据库技术经常用于更新已经部署的程序,
    因为运行脚本更行比手动更新数据库更少出错."""
    # 有一定的副作用,用户资料显示的关注者和被关注者的数量都增加了一个.为了显示准确,这些数字要减去1.例如{{ user.followers.count() - 1 }}

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


# '文章模型,博客文章包括正文,时间戳,已经和User模型的一对多关系,body字段的定义类型是db.Text,所以不限制长度.' \
# '在程序的首页要显示一个表单,以便让用户写博客,有一个多行文本输入框,用于输入博客文章的内容,还有一个提交按钮'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    body_html = db.Column(db.Text)
    # Post模型和Comments 表的一对多关系.
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    # 随机生成文章的时要为每篇文章随机指定一个用户，为此，我们使用offset()查询过滤器，这个过滤器会跳过参数中指定的记录数量，通过设定一个随机的
    # 偏移值，再调用first()方法，就能每次都能获得一个不同的随机用户。

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong',
                        'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, outpu_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)

''' 把body的md文本转换成HTML，分三步完成，首先markdown函数先把md文本转换成HTML.然后把得到的结果和允许使用的html标签列表传给clean() 函数
clean函数删除所有不在白名单中的标签，转换的最后一步，由linkify()函数完成，这个函数由Bleach提供，把纯文本的URL转换成适当的<a>链接。
最后一步是很有必要的。 因为MarkDown规范没有为自动生成链接提供官方支持。PageDown以扩展的形式实现了这个功能，因此在服务器上要调用这个函数

最后，如果post.body.html字段存在，还要把post.body换成post.body_html'''


# on_changed_body函数注册在body字段上，是SQLalchemy “set” 事件的监听程序，只要这个类实例设了新值，函数会自动被调用，
# 函数把body字段的文本渲染成HTML格式，结果保存在body_html中，自动且高效完成Markdown文本到HTML的转换。


"""
评论和博客文章没有太大区别,都有正文,作者,和时间戳.只是这个特定实现中都使用Markdown语法编写.评论属于某篇博客文章,因此定义一个从post表到
comments表的一对多关系.使用这个关系可以获取某篇特定特定博客文章的评论列表.

comments表还和user表有一对多关系,通过这个关系可以获取用户发表的所有评论,还能间接知道用户发表多少篇评论,用户发表的评论数量可以显示在用户资料页面中.

Comments模型的属性几乎和Post模型一样,不过多了多了一个disabled字段, 这是个布尔值字段,协管员可以通过这个字段查禁不当言论,和博客文章一样,
评论也定义了一个事件,在修改body字段的内容时触发,自动把markdown文本转换成HTML,装换过程和第十一章的博客文章一样,不过评论相对较短,而且对
markdown中允许使用的HTML标签要求还要严格,要删除段落相关的标签,自留下格式化字符串的标签,

为了完成对数据库的修改,User模型和Post模型还要建立与与comments 表的一对多关系,

comments = db.relationship('Comment', backref='author', lazy='dynamic')
comments = db.relationship('Comment', backref='author', lazy='dynamic')
"""


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts_id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, strip=True))

db.event.listen(Commment.body, 'set', Commment.on_changed_body)

# 出于一致性考虑,定义了 AnonymousUser 类,并实现了 can() 和 is_administrator()方法
# 这个对象继承自 AnonymousUserMixin类,并将其设为用户未登录是 current_user的值.这样程序不用先
# 检查用户是否登录.就能自由调用 current_user.can() 和 current_user.is_administrator().


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser

# 这段代码作用未明确


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))