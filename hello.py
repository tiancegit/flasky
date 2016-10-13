#!coding:utf-8
#hello.py
from flask import Flask
app = Flask(__name__)

@app.route('/')       #使用程序实例提供的app.route修饰器，把修饰的函数注册成路由
def index():          #index注册成根路由的处理程序，这个函数的返回值叫做响应。
    return '<h1>Hello world</h1>'

@app.route('/user/<name>')    #动态路由　name参数动态生成响应
def user(name):
    return '<h1>hello, %s!</h1>' % name


#print app.url_map  可以用这个方法查看URL映射，其中的‘HEAD’, 'OPTIONS', 'GET'是请求方法，Flask指定了请求方法。HEAD和OPTIONS是Flask自动处理的。

if __name__ == '__main__':   #__name__ == __main__ 是python的惯常用法，直接启动脚本才会启动开发服务器，从其它脚本引入这个hello.py,就不会执行app.run
    app.run(debug=True )      #程序实例使用run方法启动flask集成的Web开发的服务器,要是想启动调试模式，可以吧debug参数设为True.
