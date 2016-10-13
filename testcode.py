#!coding:utf-8
from flask import request   #上下文处的引入
from flask import Flask
from flask import make_response   #Response对象所用到的函数的引入
from flask import redirect     #重定向函数的的引入
from flask import abort   #处理错误abort函数的引入

app = Flask(__name__)

#
# @app.route('/')
# def index():
#     user_agent = request.headers.get('User-Agent')
#     return '<p>Your s is %s</p>' % user_agent

#Flask 使用上下文临时把一些对象变为了全局可访问，这里把request当作全局变量使用
#Flask 使用上下文让特定的变量可以在一个线程中全局访问。与此同时不会干扰其它的线程，
#Flask中又两种上下文， 程序上下文（current_app, g）,以及请求上下文（request， session）。


# @app.route('/404')
# def indexx():
#     return "<h1>Bad Request</h1>", 404
#如果视图函数要返回的响应使用不同的状态码，可以把数字当做第二个返回值，添加到响应文本之后。##404表示请求无效
#视图返回的响应,还可以接受第三个参数，一个由首部（header）组成的字典，可以添加到http响应中。

#Flask视图函数还可以返回Response对象，make_response()函数可以可以接受1个，2个或者3个参数（和视图的返回值一样，），并返回一个
#Response对象，有时候需要在视图函数中进行这种转换，然后在响应对象调用各种方法，进一步设置响应。

#下例创建了一个响应对象，并进行了cookie的调用设置


@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie</h1>')  #类似直接返回响应那样的写法，可以加状态码。
    response.set_cookie('answer', '42')   #给response设置一个cookie，可以在浏览器里看到相对应的cookie
    return response   #响应直接返回对象。

#有一种名为“重定向”的特殊响应类型。这种响应没有页面文档，只告诉浏览器一个新的地址用以加载新的页面，重新定向到新的页面。经常在Web表单中使用。
#重定向经常使用302状态码来表示，指向的地址由Location首部提供。重定向可以使用3个值的形式的返回值生成，也可以在Response中设定。
#由于使用频繁，Flask提供了redirect（）辅助函数，用于生成这种响应。例子：


@app.route('/red')
def reb():
    return redirect('http://www.zhihu.com')   # 会直接重定向到字符串的网址中去，尚未知能否站内重定向或者重定向到错误页面去，比如404页面


# 还有一种特殊的响应由abort生成，用于处理错误，下面这个例子中，如果URL中动态参数id对应的用户不存在，就返回状态码404


load_user = ('lee')


@app.route('/user/<id>')
def get_userid(id):
    user = load_user(id)
    if not user:
        abort(404)
    return '<h1>Hello %s</h1>' % user.name     # aobrt可以处理错误，不过暂时不清楚load_user的数据类型和格式没法调试成功。

# 注意，abort不会把它的控制权交给调用它的函数，而是抛出异常把控制权交给Web服务器来处理。


# app.add_url_rule('/head')    #app.add_url_rule另一种定义url的语法，暂时没搞懂，搁置。！！！！
# def head():
#     return 'hello'

if __name__ == '__main__':
    app.run(debug=True)