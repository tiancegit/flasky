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
