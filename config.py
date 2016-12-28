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
    MAIL_USERNAME = os{% extends "base.html" %}

{% block page_content %}
<div class="page-header">
    <h1>{{ user.username }}</h1>
    {% if user.name or user.location %}
    <p>
    {%  if user.name %}{{ user.name }}{% endif %}
    {% if user.location %}
    From <a href="http://map.google.com/?q={{ user.location }}">
        {{ user.location }}
    </a>
    {% endif %}
    </p>
{% endif %}
{% if current_user.is_administrator() %}
<p>
    <a href="mailto:{{ user.email }}">{{ user.email }}</a>
</p>
{% endif %}
{% if user.about_me %}
    <p>
    {{ user.about_me }}
    </p>
{% endif %}
<p>
    Member since {{ moment(user.member_since).format("L") }}. <br />
    Last seen {{ moment(user.last_seen).fromNow() }}
</p>
</div>
{% endblock %}


{# name和location字段在同一个<p>元素中渲染，只有至少定义了这两个字段中的一个时，<p>元素才会被创建。
用户的location字段会被渲染成指向谷歌地图的查询链接。
如果登录用户是管理员的话，那么显示用户的电子邮件地址，且渲染成mailto链接。#}

{# 大多数用户都希望能够轻松地访问自己的资料页面，因此我们可以在导航条中添加一个链接,对于base进行修改>> #}
.environ.get('MAIL_USERNAME')  # 千万不要把账户密码直接写入脚本,特别是准备开源的时候,为了保护账户信息,
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



