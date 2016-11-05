#jinjia2

jinjia2能识别所有类型的值，甚至是一些复杂的类型，例如列表，字典，对象。
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

下表列出来jinjia2的提供的部分常用过滤器：
| 过滤器名    | 说 明
| safe       | 渲染值时不转义
| capitalize | 把首字母转换成大写，其它字母转换成小写
| lower      | 把值转换成小写形式
| upper      | 把值转换成大写形式
| title      | 把值中的每个单词的首字母都转换为大写
| trim       | 把首字母的空格去掉
| striptags  | 渲染之前把值中的所有的 HTML标签 都删掉