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

服务器需要统一时间单位,这个用户所在的地理位置无关,所以一般使用协调世界时间(Coordinated Universal Time) UTC.
不过用户看到UTC格式的时间会感到困惑,他们更希望看到当地时间,而且采用惯用的格式.

要在服务器上只使用UTC时间,一个优雅的解决方案就是把时间单位发送给Web服务器,转换成当地时间,然后渲染,Web服务器能更好的完成这一个任务,
因为他能获取用户电脑中的时区和区域设置.

有一个使用JavaScript开发的优秀客户端开源代码库,名为moment.js(http://momentjs.com/),它可以在浏览器中渲染日期和时间,Flask-moment是
一个应用扩展,能把moment.js集成到jinja2模板中.Flask-Moment可以使用pip安装:

$ pip install Flask-moment

Flask 扩展一般都在创建程序实例是初始化.下面的是初始化方法:
```python
from flask.ext.moment import Moment  #这个是0.10的语法
#...    #Flask 0.11.1的语法是 :  from flask_Moment import Moment
moment = Moment(app)
```

除了moment.js,Flask-Moment还依赖jQuery.js.要在HTMl文档的某个地方引入这两个库,可以直接引入,还可以选择使用那么版本,也可以使用扩展提供的
辅助参数,从内容分发网络(Content Delivery Network, CDN)中引入通过测试的版本,Bootstrap已经引入jQuery.js,因此只需要引入moment.js即可.

下面的这个示例展示了如何在基模板的scripts块中引入这个库.base.html
```html
{% block scripts %}
{{ super() }}
{{ moment.inclute_moment() }}
{% endblock %}
```
千万要加上super(),不可以少了括号,如果不加这个函数,之前Bootstrap导入的jQuery.js库就会被覆盖掉,不被导入到base这个基模板中.

为了处理时间戳,Flask-Moment向模板开放了moment类,下面的这个示例把变量current_time传入了模板进行渲染.

hello.py 加入一个datetime变量
```python
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())
```

下面的示例展示了如何在模板中渲染current_time.
```html
<p>The local date and time is {{ moment(current_time).format('LLL') }}.</p>
    <P>That was {{ moment(current_time).fromNow(refresh=True)}}</P>
```

format('LLL')根据客户端电脑中的时区和区域设置渲染的日期和时间.参数决定了渲染的方式,'L'到"LLLL"分别对应了不同的复杂度,format()函数
还可以接受自定义格式说明符.

第二行的fromNow()渲染相对的时间戳,而且会随着时间的推移自动刷新显示的时间.这个时间戳最开始显示的为'a few seconds ago',但指定refresh参数后.
其内容会随着时间的推移而更新,如果一直待在那个界面,几分钟后,会看到显示的文本变成'a minute ago' '2 minute ago'等.

Flask-Moment实现了moment.js中的format(),fromNow(),fromTime(),calendar(),valueOf()和unix()方法,可以查阅文档
文档地址:(http://momentjs.com/docs/#/displaying/) 学习moment.js 提供的全部格式化选项.

注意: Flask-Moment假定服务器端程序处理的时间戳是纯正的datetime对象,且用UTC表示.关于纯正和细致的日期和时间对象的说明,
请阅读标准库中datetime包的文档(https://docs.python.org/2/library/datetime.html).


Flask-Moment渲染的时间戳可以实现多种语言的本地化,语言可以在模板中选择,把语言代码传给lang()函数即可:
    {{ moment.lang('es') }}

译者注:纯正的时间戳,英文为navie time.指不包含时区的时间戳.细致的时间戳,英文为 aware time.指包含时区的时间戳.






















