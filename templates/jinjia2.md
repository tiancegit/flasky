##jinja2

jinja2能识别所有类型的值，甚至是一些复杂的类型，例如列表，字典，对象。
在模板中使用变量的部分示例如下：
```html
<p>A value from a dicrionary: {{ mydict['key'] }}.</p>
<p>A value from a list:{{ mylist[3] }}.</p>
<p>A value from a list, with a variable index:{{ mylist[myintvar] }}.</p>
<p>A value from a object's method:{{ myobj.somemethod() }}.</p>
```


可以使用过滤器修改变量，过滤器添加到变量名之后，中间使用竖线分隔，
例如下述的模板以首字母大写形式显示了变量name的值：
```
Hello,{{ name|capitalize }}
```

下表列出来jinja2的提供的部分常用过滤器：
| 过滤器名    | 说 明
| safe       | 渲染值时不转义
| capitalize | 把首字母转换成大写，其它字母转换成小写
| lower      | 把值转换成小写形式
| upper      | 把值转换成大写形式
| title      | 把值中的每个单词的首字母都转换为大写
| trim       | 把首字母的空格去掉
| striptags  | 渲染之前把值中的所有的 HTML标签 都删掉


safe 过滤器说明。
```
默认情况下，出于安全考虑，jinja2 会转义所有的变量，例如一个变量的值，为<h1>Hello world</h1>。  
jinja2会渲染成 <h1>Hello world</h1>, 而不是显示为标题。浏览器会显示这个 “<h1> Hello world”  
但不会解释为标题元素。很多情况下，需要显示变量中储存的HTML代码时，就可以使用safe过滤器。
```
**千万不要在不可信的值上使用safe过滤器，例如用户在表单中输入的文本。**

###jinja 提供了多种控制结构哦，可以用来改变模板的渲染流程。

####如何在模板中使用条件控制语句：

```html
{% if user %}
    Hello, {{ user }}!
{% else %}
    Hello,Stranger!
{% endif %}
```

####另一种常见需求就是在模板中渲染一组元素，如何使用for循环实现：

```html
<ul>
    {% for comment in comments %}
        <li>{{ comment }}</li>
    {% endfor %}
</ul>
```

####jinja2 支持宏，宏类似python代码中的函数，例如：
```html
{% macro render_comment(comment) %}
    <li>{{ comment }}</li>
{% endmacro %}

<ul>
    {% for comment in comments %}
        {{ render_comment(comment) }}
    {% endfor %}
</ul>
```

为了可以重复使用宏，可以保存为单独的文件，然后在需要的模板中导入：
```
{% import 'macros.html' as macros %}
<ul>
    {% for comment in comments %}
        {{ macros.render_comment(comment) }}
    {% endfor %}
</ul>
```


需要在多处重复使用的模板代码片段可以写入单独的文件,再包含在所有模板中,以避免重复.

    {% include 'common.html' %}

####模板继承

另一种重复使用代码的强大方式就是模板继承,它类似于Python代码中的类继承.  
首先,创建一个名为base.html的基模板:
```html
<html>
<head>
    {% block head %}
        <title>{% block title %}{% endblock %} - My Application</title>
    {% endblock %}
</head>
<body>
{% block body %}
{% endblock %}
</body>
</html>
```

block 标签定义的元素可以在衍生模板中修改,在本例中,定义了名为head,title和body的块.  
注意,title 包含在head块中.下面的实例就是基模板的衍生模板.
```html
{% extends 'base.html' %}
{% block title %}Index{% endblock %}
{% block head %}
    {{ super() }}
    <style>
    </style>
{% endblock %}
{% block body %}
<h1>Hello,world!</h1>
{% endblock %}
```

extends 指令声明了这个模板衍生自base.html.在extend指令之后,基模板中的三个块被重定义.  
模板引擎会将其插入适应的位置,注意新定义的head块,在基模板中其内容不是空的.  
所以使用super()来获取原来的内容.

####使用Flask-Bootstrap集成Twitter Bootstrap

Bootstrap是客户端框架.因此并不会涉及服务器.服务器要做的只是提供引用了Bootstrap  
层叠样式表(CSS)和JavaScript文件的HTML响应.并在html,CSS和JavaScript代码中实例化  
所需组件.

使用 Flask-Bootstrap的Flask扩展.简化集成的过程. Flask-Bootstrap使用 pip 安装:

(venv) $ pip install Flask-bootstrap

Flask 扩展一般都在创建程序实例是初始化.下面的是初始化方法:  
```python
from flask.ext.bootstrap import Bootstrap  #这个是0.10的语法
#...    #Flask 0.11.1的语法是 :  from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
```

初始化Flask-Bootstrap之后,就可以在程序中使用一个包含所有Bootstrap文件的基模板.  
这个基模版利用了jinja2的模板继承机制.让程序可以扩展为一个具有基本页面结构的基模板,  
其中就有用来引入Bootstrap元素.  
示例是把user.html改写成衍生模板后的新版本.
```html
{% extends "bootstrap/base.html" %}

{% block title %}Flasky{% endblock %}

{% block navbar %}
    <div class="navbar navbar-inverse" role="navigation">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" 
                data-toggle="collapse" data-target = ".navbar-collapse">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">Flasky</a>
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/">Home</a> </li>
                </ul>
            </div>
        </div>
    </div>
{% endblock %}

{% block content %}
<div class="container">
    <div class="page-header">
        <h1>Hello,{{ name }}!</h1>
    </div>
</div>
{% endblock %}
```

jinja2 中的extends指令  从Flask-Bootstrap中导入Bootstrap/base.html.从而实现模板继承.  
Flask-Bootstrap中的基模板提供了一个网页框架.引入了Bootstrap中的所有CSS和JavaScript文件.

基模板定义了可在衍生模板中使用重定义的块.block和endblock指令定义的块的内容可添加到基模板中.

上面的user.html模板定义了三个块.分别命名为 title navbar 和content.这些块都是基模板提供的,  
可以在衍生模板中重新定义.title的作用,其中的内容会出现在渲染后的html文档的头部.  
navbar和content这两个块分别表示页面中的导航条和主题内容.

这个模板中,navbar块使用Bootstrap组件自定义了一个简单的导航条,content块中有个  
div容器.其中包含一个页面头部,之前版本的模板中的欢迎信息,现在放在了这个页面头部.


Flask-Bootstrap的base.html还定义了很多其它块.都可以在衍生模板中使用.  
下表列出了所有可用的块.
```
doc             | 整个html文档
html_attribs    | <html>标签的属性
html            | <html>标签的内容
head            | <head>标签的内容
title           | <title>标签的内容
metas           | 一组<meta>标签
style           | 层叠样式表定义
body_attribs    | <body>标签的属性
body            | <body>标签的内容
navbar          | 用户定义的导航条
content         | 用户定义的页面内容
scripts         | 文档底部的JavaScript声明
```


上表的很多块都是Flask-Bootstrap自用的.如果直接重新自定义可能会导致一些问题.  
例如,Bootstrap所需的文件在style和scripts块中声明的.如果程序需要想已经有内容的模块中  
添加新内容,必须使用Jinja2提供的super()函数,例如,如果在衍生模板中添加新的JavaScript文件,  
需要这样定义scripts块.

{% block scripts %}
{{ super() }}
    <script type="text/javascript" src="my-script.js"></script>
{% endblock %}

(个人理解,要先用super()函数来获取原来基模板的style和JavaScript文件,再在后面添加新内容.)


####自定义错误页面
如果在浏览器的地址栏输入了不可用的路由,会显示一个状态码为404的错误页面.  
现在这个页面太简陋了,样式和使用了Bootstrap的页面不一致.

像常规路由那样,Flask允许程序使用基于模板的自定义错误页面.常见的错误代码有两个:
404,客户端请求未知页面或者路由时显示.
500,有未处理的异常时显示.
为这两个错误代码指定自定义处理页面的方式如下:
```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
```

和视图函数一样,错误处理程序也会返回响应.它们还返回与该错误对应的数字状态码.  
错误处理程序中引用的模板也要编写,这些模板应该和常规的页面使用一样的布局,  
因此要有一个导航条和显示错误信息的页面头部.

jinja2的继承机制可以帮助我们做到这一点.Flask-Bootstrap提供了一个具有页面基本布局的基模板.
其中包含导航条,同样,程序可以定义一个具有更完整页面布局的基模板,其中包含导航条,  
而页面内容则可以留到了衍生模板中定义.

下面的例子展示了templates/base.html的内容.这是一个继承自Bootstrap/base.html的新模板.  
其中定义了导航条.这个模板本身可以作为别的模板的基模板.例如404.html,500.html,user.html

templates/base.html:

```
```






