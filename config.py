#!coding:utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))  # 获取文件路径


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lee'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")  # 这是管理员邮箱,只要当这个地址出现在注册请求中,就会被赋予正确的角色.
    # 邮件配置
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = '587'
    MAIL_USE_TLS = True  # SMTP 服务器好像只需要TLS协议
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 千万不要把账户密码直接写入脚本,特别是准备开源的时候,为了保护账户信息,
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 可以使用脚本从环境中导入敏感信息
    # app.config["MAIL_USE_SSl"] = True  #这是需要 SSL协议的设置，不需要：详细见https://support.google.com/a/answer/176600?hl=zh-Hans

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 基类Config中包含了通用配置，子类分别定义了专用的配置，如果需要，可以添加其他配置类。
# 为了配置方式灵活安全，某些配置可以从环境变量中导入，例如 SECRET_KEY的值，这是个敏感信息，可以在环境中设定，也可以在系统中
# 设置一个默认值以防环境中没有定义。


''' 在三个子类中，SQLALCHEMY_DATABASE_URL变量指定了不同的值，这样程序就可以在不同的配置运行，每个环境都使用不用的数据库。

配置类可以定义init_app()类方法，其参数是程序示例，在这个方法中，可以执行对当前环境的配置初始化。

在程序的末尾，config字典中注册了不同的胚子环境，而且还注册了一个默认配置。（本例的开发环境）

'''



