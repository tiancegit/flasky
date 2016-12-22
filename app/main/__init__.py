#! coding:utf-8
from flask import Blueprint

from ..decorators import Permission

main = Blueprint('main', __name__)

from . import views, errors

'''
在模板中可能也需要检查权限,所以 Permission 类为所有位定义了变量.为了避免每次调用 render_template()时多添加一个参数,
可以使用上下文,上下文处理器能使变量在所有模板中全局可访问.
修改app/main/__init__.py: 把 Permission 类加入模板上下文.
'''


@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)
