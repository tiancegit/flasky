#!coding:utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
# 登录login的设置
login_manager = LoginManager()
login_manager.session_protection = 'strong'   # LoginManager 对象的 session_protection 属性可以设为 None 、 'basic' 或 'strong'
login_manager.login_view = 'auth.login'       # ,以提供不同的安全等级防止用户会话遭篡改。设为 'strong' 时,Flask-Login 会记录客户端 IP
                                              # 地址和浏览器的用户代理信息,如果发现异动就登出用户。 login_view 属性设置登录页面的端点。


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 登陆页面
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app


'''
构造文件导入了大多数正在使用的 Flask 扩展。由于尚未初始化所需的程序实例,所以没
有初始化扩展,创建扩展类时没有向构造函数传入参数。 create_app() 函数就是程序的工
厂函数,接受一个参数,是程序使用的配置名。配置类在 config.py 文件中定义,其中保存
的配置可以使用 Flask app.config 配置对象提供的 from_object() 方法直接导入程序。至
于配置对象,则可以通过名字从 config 字典中选择。程序创建并配置好后,就能初始化
扩展了。在之前创建的扩展对象上调用 init_app() 可以完成初始化过程。
'''

