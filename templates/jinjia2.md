#jinjia2

jinjia2能识别所有类型的值，甚至是一些复杂的类型，例如列表，字典，对象。
在模板中使用变量的部分示例如下：
```html
<p>A value from a dicrionary: {{ mydict['key'] }}.</p>
<p>A value from a list:{{ mylist[3] }}.</p>
<p>A value from a list, with a variable index:{{ mylist[myintvar] }}.</p>
<p>A value from a object's method:{{ myobj.somemethod() }}.</p>
```