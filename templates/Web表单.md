##Web表单

尽管Flask的请求对象提供的信息足够用于处理表单,但是有些任务很单调,而且要重复操作,比如生成表单的HTML代码和验证表单提交的数据.

Flask-WTF(http://pythonhosted.org/Flask-WTF/)扩展可以把处理Web表单的过程变成一种愉悦的体验,这个扩展对独立的WTForms
(http://wtforms.simplecodes.com)包进行了打包,方便集成到Flask程序中.

Flask_WTF及其依赖可使用pip安装:
    $ pip install Flask-wtf

####跨站请求伪造保护

默认情况下,Flask-WTF能保护所有表单免受跨站请求伪造(Cross-Site Request Forgery,CSRF)的攻击,恶意网站把请求发送到被攻击者已登录的
其它网站是就会引发CSRF攻击.

为了实现CSRF保护,Flask-WTF需要程序设置一个密钥.Flask_WTF使用这个密钥生成加密令牌,再用令牌验证请求中表单数据的真伪,设置密钥的方法如下所示:
hello.py 设置Flask-WTF
```python
app = Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'
```

app.congfig字典可以用来储存框架,扩展,和程序本身的配置变量.使用标准的字典语法就能把配置值添加到app.config对象中,这个对象提供了一些方法,  
可以从文件中或环境中导入配置值.
SECRET_KEY配置的是通用密钥,可以在Flask和多个第三方扩展中使用,如其名所示,加密的强度取决于变量值的机密程度.不同的程序要使用不同的密钥.  
而且要保证其它人不知道你所使用的字符串.

为了增强安全性,密钥不应该直接写入代码,而要保存到环境变量中.

####表单类

使用Flask-WTF时,每个Web表单都由一个继承自Form的类表示,这个类定义了表单中的每一组字段.每个字段都要用对象表示,字段对象可附属一个或多个验证函数,  
验证函数用来验证用户提交的输入值是否符合要求.

下例是一个简单的Web表单,包含一个文本字段,和一个提交按钮.

hello.py  定义表单类.
```
from flask_wtf import Form   #导入表单模块
     上一句的写法错误了,应该FlaskForm 
     from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameFrom(Form):
这一句应该是
class NameFrom(FlaskForm)
    name = StringField('what is your name?', validators=[Required()])
    submit = SubmitField('Submit')
```

这个表单中的字段都定义为类变量.类变量的值是相应字段类型的对象,在这个示例中,NameForm 表单中有一个名为name的文本字段和一个名为submit的  
提交按钮.StringField类表示属性为type='text'的<input>元素.SubmitField类表示属性为type='Submit'的<input>元素.字段构造函数的第一个参数  
是把表单渲染成HTML是使用的符号.

StringField构造函数中的可选参数的validators指定一个由验证函数组成的列表,在接受用户提供的数据之前验证数据.验证函数Required是确保提交的字段不为空.  

*Form基类由Flask-WTF扩展定义,所以从Flask_wtf中导入,字段和验证函数却直接可以从WTF包中导入.

WTForms支持的HTML标准字段如下所示.
```
 字段类型               说明
StringField      |   文本字段
TextAreaField    |   多行文本字段
passwordField    |   密码文本字段
HiddenField      |   隐藏文本字段
DataField        |   文本字段,值为datetime.date格式.
DataTimeField    |   文本字段,值为datetime.datetime格式
IntegerField     |   文本字段,值为整数
DecimalField     |   文本字段,值为decimal.Decimal
FloatField       |   文本字段,值为浮点数
BooleanField     |   复选框,值为True和False
RadioField       |   一组单选框
SelectField      |   下拉列表
SelectMultipleField  下拉列表,可选择多个值.
FileField        |   文件上传字段.
SubmitField      |   表单提交按钮
FromField        |   把表单作为字段,嵌入另一表单.
FieldList        |   一组指定类型的字段. 
```

WTF内建的验证函数,如表所示.

```
验证函数                  说明
Email         |     验证电子邮件地址
EqualTo       |     比较两个字段的值,常用于输入两次密码进行确认的场景.
IPAddress     |     验证IPv4网络地址
Length        |     验证输入字符串的长度
NumberRange   |     验证输入值在数字范围内.
Optional      |     无输入值时跳过其他验证函数.
Required      |     确保字段中有数据(不为空)
Regexp        |     使用正则表达式去验证输入值.
URL           |     验证URL
AnyOf         |     确保输入值在可选值列表中
NoneOf        |     确保输入值不在可选值列表中.
```


####把表单渲染成HTML

表单字段是可调用的,在模板中调用后会渲染成HTML.假设视图函数把一个NameForm实例通过参数Form传入模板中,在模板可以生成一个简单的表单.
```
<form method="post">
    {{ form.hidden_tag() }}
    {{ form.name.label }}{{ form.name() }}
    {{ formsubmit() }}
</form>
```

要想改进表单的外观,可以把参数传进渲染字段的函数,传入的参数会被转换成字段的HTML属性,力图,可以为字段指定id或者class属性.然后定义CSS样式.
```
<form method="POST">
    {{ form.hidden_tag() }}
    {{ form.name.label }}{{ form.name(id='my-text-field') }}
    {{ form.submit() }}
</form>
```

即便能指定HTML属性,但按照这种方式渲染表单的工作量还是很大的,所以在条件允许的情况下,最好能使用Bootstrap中的表单样式.Flask-Bootstrap提供了  
一个非常高端的辅助函数,可以使用Bootstrap中预先定义好的表单样式去渲染整个Flask-WTF表单,而这些操作秩序一次调用即可完成.使用Flask-Bootstrap.  
上述表单可以使用下面的方式渲染.
```
{% import 'bootstrap/wtf.html' as wtf %}
{{ wtf.quick_form(form) }}
```
import 指令的使用方法和普通Python代码一样,允许导入模板元素,并用在多个模板中,导入的Bootstrap/wtf.html,文件中定义了一个使用Bootstrap  
渲染Flask-WTF表单对象的辅助函数.wtf.quick_form()函数的参数为Flask-WTF表单对象.使用Bootstrap的默认样式渲染传入的表单.hello.py的完整模板如下:  
```
{% extends "base.html" %}

{% block title %}Flasky{% endblock %}

{% block page_content %}
<div class="page-header">
    <h1>Hello,{% if name %} {{ name }}{% else %} Stranger {% endif %}!</h1>
</div>
    {{ wtf.quick_form(from) }}
{% endblock %}
```

模板的内容区有两部分,第一部分是头部,显示欢迎信息.这里用到了一个模板条件语句.jinja2中的条件语句格式为{% if condition%}...{% else %}  
...{% endif %}   如果条件的计算结果为True,那么渲染if和else指令之间的值.如果条件的计算结果False,则渲染else和endif之间的值.在这个例子中.  
如果没有定义模板变量name,则渲染字符串'Hello, Stranger!'.内容区的第二部分使用wtf.quick_form()函数,渲染NameFrom对象.



###在视图函数中处理表单

在新版hello.py中,视图函数index()不仅仅要渲染表单,还要接受表单中的数据.下面这个就是更新后的index()视图函数:  
```Python
@app.route('/', methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.date = ''
    return render_template('index.html', form=form, name=name)
```


app.route修饰器中添加的methods参数告诉Flask在url映射中把这个视图函数注册为GET和POST请求的处理程序,如果没指定methods参数,  
就只把视图函数注册为GET请求的处理程序.

把post加入方法列表,因为将提交表单作为POST请求进行处理更方便些.表单也可以作为get请求提交.不过GET请求没有主体.提交的数据以查询字符串的形式  
附加到Url中,可以在浏览器地址栏中看到,基于这个原因以及其他多个原因,提交表单大都作为POST请求处理.

局部变量用于存放表单中输入的有效名字,如果没有输入,其值为None,如上述代码,在视图中创建一个NameForm的类实例用于表示表单,提交表单之后,如果数据能被  
所有验证函数接受,那么validate_on_submit的返回值为True,否则返回False.这个函数的返回值决定了是重新渲染表单还是处理表单的数据.

用户第一次访问程序时,服务器会收到一个没有表单数据的get请求,所以validate_on_submit()将返回False.if的语句将被跳过.通过模板渲染请求,并传入表单和值为None  
的name变量作为参数,用户会看到浏览器显示一个表单.

用户提交表单后,服务器将收到一个包含数据的POST请求,validate_on_submit()会调用name字段上附属的Required()验证函数,如果名字不为空,  
就能通过验证,validate_on_submit()返回True.现在用户输入的名字可以通过字段的date属性获取.在if语句中,把名字赋值给局部变量name.  
然后再把date属性设为空字符串,从而清空表单字段.最后一行会调用render_template()函数渲染该模板,但这一次参数的值为表单输入的名字.  
因此会显示一个针对该用户的欢迎信息.


###重定向和用户回话

最新版的hello.py有一个可用性问题.用户输入名字后提交表单,然后点击浏览器的刷新按钮,会看到一个莫名其妙的警告.要求在再次提交表单之前进行确认.  
之所以出现这个情况.是因为刷新页面的时间,浏览器会重新发送之前已经发送过的最后一个请求.如果这个请求是一个包含表单数据的POST请求的话,刷新页面后  
会再次提交表单.大多数情况下,并不是理想的处理方式.

很多用户都不了解浏览器的这个警告.基于这个原因,最好别让Web程序把POST请求作为最后一个请求.

这种需求的实现方式是,是重定向作为Post请求的响应.而不是使用常规响应.重定向是一种特殊的相应.响应内容是URL,而不是包含HTML代码的字符串.  
浏览收到这种响应的时候,会像重定向的URL发起get请求.显示页面的内容.这个页面的加载要多花几微秒.因为要把第二个请求发送给服务器.除此之外,  
用户不会察觉到有什么不同.现在,最后一个请求是一个get请求,所以刷新命令可以像预期那样正常使用了.这个巧称  POST / 重定向 / GET 模式.

但这个方法会带来另一个问题.程序处理Post请求的时候,使用form.name.data获取用户输入的名字,但是一旦这个请求结束了,数据也就丢失了.因为这个  
POST请求使用重定向处理.所以程序需要保存输入的名字.这样重定向的请求才能获得并使用这个名字.从而构建真正的响应.

程序可以把数据存储在用户会话中.在请求之间"记住"数据.用户会话是一种私用存储,存在每一个连接到服务端的客户端中.用户会话,它是请求上下文的变量.
名为session,像标准的Python字典一样操作.

* 默认情况下,用户会话保存在客户端cookie中,使用设置的SECRET_KEY进行加密签名.如果篡改了cookie中的内容,签名就会失效.会话随之失效.

下例是index()函数的新例子.实现了重定向和用户会话.  hello.py
```Python
from flask import Flask, render_template, session, redirect, url_for

@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for("index"))
    return render_template('index.html', form=form, name=session.get('name'))
```


在之前的一个版本里,局部变量name被用于存储用户在表单中输入的名字.这个变量现在保存在用户会话中,即是session['name'],所以在两次请求中也能  
记住输入的值.

现在,包含是\合法表单数据的请求最后会调用redirect()函数.redirect()是个辅助函数,用于生成http重定向响应.redirect()函数的参数是重定向的URL.  
这里使用的重定向URL是程序的根地址.因此重定向响应本可以写得更简单些,写成redirect('/'),但是却会使用Flask提供的url生成函数url_for()  
推荐使用url_for函数生成URL,因为这个函数可以使用url映射生成URL映射生成URL,从而保证了URL和定义的路由兼容,而且修改路由名字后也依然可用.

url_for()函数的第一个且唯一必须指定的参数是端点名.即路由的内部名字,默认情况下,路由的端点是相应视图函数的名字.上例中,处理根路由的视图函数是index()  
因此,传给url_for函数的名字是index. 

最后一处改动位于 render_template()函数中.使用session.get('name')直接从会话中读取name参数的值.和普通的字典一样,这里使用get()获取字典  
中键相对应的值,以避免未找到键的异常情况,因为对于不存在的键,get()会返回默认值None.


####Flash消息

请求完成之后,有时需要用户知道状态发生了变化,这里可以使用确认信息,警告或者错误提醒,一个典型的例子是,用户提交了一项有错误的表单后,服务器发回的响应  
重新渲染了表单.并在表单显示一个信息,提示用户用户名或密码错误.

这是Flask的核心特性,如下列所示,flash()函数可以实现这种效果.
```python
from flask import Flask, render_template, session, redirect, url_for, flash

@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session["name"] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))
```


在这个示例中，每次提交的名字都会和存储在用户会话中的名字进行比较，而会话中存储的名字是前一次在这个表单中提交的数据。如果两个名字不一样，就会
调用flash函数在给发给客户端的下一个相应中显示一个消息。

仅调用flash()函数并不能把消息显示出来，程序使用的模板要渲染这些消息，最好在基模板中渲染flash消息。因为这样所有的页面都能使用这些消息，
Flask把get_flashed_messages()函数开放给模板，用来获取并渲染消息。
```html
{% block content %}
<div class="container">
{% for message in get_flashed_messages() %}
<div class="alert-warning">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    {{ message }}
</div>
{% endfor %}
{% block page_content %}{% endblock %}
</div>
{% endblock %}

```

在模板中使用循环是因为在之前的请求循环中每次调用flash()函数时都会生成一个消息，所以就可能有多个消息在排队等候显示。get_flashed_messages()
函数获取的消息在下次调用时不回再次返回。因此flash消息只显示一次，然后就消失了。

从表单中获取用户输入是大多数程序都需要的功能，把数据保存在永久储存器也是一样。




















