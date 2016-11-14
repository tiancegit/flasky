##链接
任何具有多个路由的链接的程序都需要连接不同页面的链接,例如导航条.

在模板中直接编写简单路由的URl链接并不难,但对于包含可变部分的动态路由,在模板中构建正确的路由就很困难,而且直接编写URL会对代码定义的路由产生
不必要的依赖关系.如果重新定义路由,模板中的链接就可能会失效.

为了避免这些问题,Flask提供了url_for辅助函数,它可以使用程序url映射中保存的信息生成URL.

url_for()函数最简单的用法是以视图函数名(或者app.add_url_route()定咦路由是使用的端点名)作为参数,返回对应的URl,例如:
在当前版本的hello.py中调用url_for("index")得到的结果是/.调用url_for("index",_external=True)返回的则是绝对地址,在这个示例中是
"http://localhost:5000/"

#####注意:生成链接程序内不同路由的链接是,使用相对地址就够了.如果生成在浏览器之外使用的链接,则必须使用绝对地址,例如在电子邮件发送的链接.

使用url_for()生成动态地址时,将动态部分作为关键字参数传入,例如.url_for('user', name="jhon", _externl=True)的返回结果是:
"http://localhost:5000/user/john".

传入url_for()的关键字参数不仅限于动态路由的参数,函数能将任何额外参数添加到查询字符串中,例如.url_for('index',page=2)的返回结果是/?page=2.

##静态文件

Web程序不是仅由Python代码和模板组成.大多数程序还会使用静态文件,例如HTMl代码中引用的图片.JavaScript源码文件和CSS.

static路由,对静态文件的引用被当成一个特殊的路由,即/static/<filename>.例如,调用url_for("static",filename='css/style.css', _external=True
得到的结果是http://localhost:5000/static/css/style.css.

默认设置下,Flask在程序根目录中名为static的子目录中寻找静态文件,如果需要,可在static文件夹中使用子文件夹存放文件,服务器收到前面的这个URL后,
会生成一个响应,包含文件系统中static/css/style.css文件的内容.

下面的示例展示了如何在程序的基模板中放置favicon.ico图标,这个图标会显示在浏览器的地址栏中:
template/base.html:  定义收藏夹图标

```html
{% block head %}
{{ super() }}
<link rel="shortcut icon" href="{{ url_for('static', filename = 'favicon.ico')}}" type="image/x-icon">
<link rel="icon" href="{{ url_for('static', filename = 'favicon.ico') }}" type="image/x-icon">
{% endblock %}
```
图标的声明会插入head块的末尾,注意如何使用super()保留基模板中定义的块的原始内容.

##使用Flask-Moment本地化日期和时间.

如果Web程序的用户来自世界各地,处理日期和时间可不是一个简单的任务.

服务器需要统一时间单位,这个用户所在的地理位置无关,所以一般使用协调世界时间(Coordinated Universal Time)