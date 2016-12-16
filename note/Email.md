##电子邮件
很多类型的应用程序都需要在特定事件发生时去提醒用户,而常用的通信方式就是电子邮件.虽然Python标准库中的 smtplib包可用于Flask程序中发送邮件,  
但包装了smtplib的Flask-Mail扩展能更好的和Flask集成 

#### 使用 Flask-mail提供电子邮件支持

使用 pip 安装 Flask-Mail:  
$ pip install flask-mail

Flask-Mail链接到简单邮件传输协议(Simple Mail Transfer Protoclo, SMTP)服务器,并把邮件交给这个服务器发送,如果不进行配置,Flask-Mail  
会连接到localhost上的端口25,无需验证即可发送电子邮件,表6-1列出了可用来设置SMTP服务器的配置.

```
配置              默认值             说明
MAIL_SERVER     localhost         电子邮件服务器的主机名或者IP地址
MAIL_PORT         25              电子邮件服务器的端口
MAIL_USE_TLS    False             启用传输层安全(Transport Layer Security, TSL)协议
MAIL_USE_SSL    False             启用安全套接层(Secure Sockets Layer, SSL)协议
MAIL_USENAME     None             邮件账户的用户名
MAIL_PASSWORD    None             邮件账户的密码
```

如果连接到外部SMTP服务器,则可能更方便,举个例子,下例展示了如何配置程序,以便使用Google Gmail账户发送电子邮件.hello.py
```python
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True   #SMTP 服务器好像只需要TLS协议
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')    # 千万不要把账户密码直接写入脚本,特别是准备开源的时候,为了保护账户信息,
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')    # 可以使用脚本从环境中导入敏感信息
# app.config["MAIL_USE_SSl"] = True  #这是需要 SSL协议的设置，不需要：详细见https://support.google.com/a/answer/176600?hl=zh-Hans
```

环境变量的设置  
    
    MAIL_USERNAME = XXXX@gmail.com
    MAIL_PASSWORD = password       #不需要加单引号
    
示例：在shell中进行邮件的发送测试
```
$ export  ALL_PROXY=socks5://127.0.0.1:1080     #国内墙的缘故，要设定代理命令，走SS的代理服务

$ export MAIL_USERNAME=xxx@gmail.com
$ export MAIL_PASSWORD=password

>>> from flask_mail import Message
>>> from hello import mail
>>> msg = Message('test subject', sender='tiance1984@gmail.com', recipients=['tiance.1984@gmail.com'])
>>> msg.body = "text body"
>>> msg.html = "<b>HTML</b> body"
>>> with app.app_context():
...     mail.send(msg)
... 
```

测试得知，同一个邮件好像只可以发送一次，第二次进行 mail.send(msg)的话，服务器不会进行发送，要修改了msg的内容才可以进行第二次发送  
需要在gmail的设置中开启POP和IMAP的设置,测试中出现503错误，可以选择在https://support.google.com/mail/?p=WantAuthError 中排查可能的因素  
墙内的连接gmail不一定稳定，经常出现 网络不可达错误， 不知道国外的服务器的效果怎样，待测试。
测试了搬瓦工的VPS，可行，第一次请求谷歌会认为是别人知道了密码尝试登录，得根据邮件的连接去信任一下IP！
在墙内使用了SS代理，让终端走SS的代理的命令/该方式有效的解决了墙的问题。偶尔会因为陌生IP而被谷歌拦截请求，只需要在谷歌邮件中同意该设备就可以了。

    export  ALL_PROXY=socks5://127.0.0.1:1080

下面进行 163的设置:


    待定，，不知名原因：设置不了
    

### 在程序中集成发送电子邮件功能
为了避免每次都手动编写电子邮件消息，我们最好把程序发送邮件的通用部分抽象出来，定义成一个函数，这样做有一个好处，   
既是这个函数可以使用jinja2模板渲染邮件正文，灵活性极高，具体例子如下所示。  
hello.py
```python
app.config['FLASK_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASK_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'

def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASK_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

```

这个函数用到了两个程序特定配置项，分别定义了邮件主题的前缀，和发送人的地址，send_mail函数的参数分别为收件人地址，主题，  
渲染邮件正文的模板，和关键字参数列表，指定模板时还不能包含扩展名，这样才能用两个模板分别渲染纯文本正文和富文本正文，调用者  
将关键字参数传给render_templeate()函数，以便在模板中使用。进而生成电子邮件正文。

index()函数很容易被扩展，这样每当表单接收新名字时，程序都会给管理员发送一封电子邮件：
```
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_ADMIN']:
                send_mail(app.config['FLASK_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))
```

电子邮件的收件人保存在环境变量FLASKY_ADMIN中，在程序启动过程中，它会加载到一个同名配置变量中，我们要创建两个模板文件，分别用于  
渲染纯文本和HTML版本的邮件正文，这两个模板文件都会保存在template文件夹下的mail子文件夹中，以便和普通模板区分开来，电子邮件的模板中  
要有一个参数是用户，因此调用send_mail()函数是要以关键字参数的形式传入用户。


### 异步发送邮件

如果发送了几封邮件，mail.send()函数在发送邮件时停滞了几秒，在这个过程中，浏览器像无响应一样，为了避免处理过程中不必要的延迟，我们可以把  
发送邮件的函数移到后台线程中，修改方法如下所示：

```
frm threading import Thread

def send_async_email(app, msg):
    with app.app_context(msg):
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASK_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
```


上述的实现设计一个有趣的问题，很多flask扩展都假设已经存在激活的程序上下文和请求上下文。Flask-Mail的send（）函数使用current_app,因此必须 
激活上下文不过在不同的线程中执行mail.send()函数是，程序的上下文要使用app.app_context()人工创建。

如果程序需要发送大量的电子邮件时，使用专门发送电子邮件的作业要比给每一个邮件新建一个线程更合适，例如，我们可以把执行 send_async_email()函数的  
操作发给 Celery(http://www.celeryproject.org/)任务队列。


























