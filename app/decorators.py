#!coding:utf-8

from functools import wraps

from flask import abort
from flask_login import current_user

from .models import Permission

'''
如果想让视图函数只对有特定的权限的用户开放, 可以使用自定义的修饰器.实现了两个修饰器.
一个用于检查常规权限,一个专门用来检查管理员权限.
'''


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

# 这两个修饰器都使用了Python标准库的functools包,如果用户不具有指定权限,则返回403错误,即是 Http"禁止"
# 错误,需要添加一个 403 界面.





