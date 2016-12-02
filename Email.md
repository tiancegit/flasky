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


```