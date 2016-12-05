#!coding:utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


'''
构造文件导入了大多数正在使用的 Flask 扩展。由于尚未初始化所需的程序实例,所以没
有初始化扩展,创建扩展类时没有向构造函数传入参数。 create_app() 函数就是程序的工
厂函数,接受一个参数,是程序使用的配置名。配置类在 config.py 文件中定义,其中保存
的配置可以使用 Flask app.config 配置对象提供的 from_object() 方法直接导入程序。至
于配置对象,则可以通过名字从 config 字典中选择。程序创建并配置好后,就能初始化
扩展了。在之前创建的扩展对象上调用 init_app() 可以完成初始化过程。
'''

