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
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameFrom(Form):
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

```














