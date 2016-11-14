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


