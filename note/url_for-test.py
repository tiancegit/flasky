#!coding:utf-8

#测试url_for函数的用法


from flask import Flask, url_for
app = Flask(__name__)

@app.route("/")
def index():
    pass

@app.route("/lodgin")
def login():
    pass

@app.route("/user/<username>")
def profile(username):
    pass

with app.test_request_context():
    print url_for("index")
    print url_for("login")
    print url_for("login", next='/')
    print url_for("profile", username="John Doe")

    #暂时搞不懂其中的用法和原理,先搁置
    #与testcode.py中的app.add_url_rule用法貌似有相关联的地方.待解决

app.run()