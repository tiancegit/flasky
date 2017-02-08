#!coding:utf-8
from flask import render_template, redirect, url_for, current_app, abort, flash, request, make_response
from flask_login import login_required, current_user

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostFrom, CommentForm
from .. import db
from ..decorators import admin_required, permission_required
from ..models import User, Role, Permission, Post, Comment

# 函数把表单和完整的博客文章列表传给模板，文章列表按照时间戳进行降序排序，博客文章表单采取了惯常的处理方式，如果提交的数据通过
# 验证就创建一个新的Post实例。在发表文章之前，要检查当前用户是否有写文章的权限。
'''
决定显示所有博客文章还是只显示关注用户文章的选项存储在cookie的show_follow字段中.如果其值是非空字符串.则表示只显示所关注用户的文章.
cookie以request.cookie字典的形式存储在请求对象中,这个cookie的值会转换成布尔值,根据得到的值设定本地变量query的值.
query决定了最终获取所有博客文章的查询.或是获取过滤后的博客文章查询.显示所有用户的文章时要使用顶级查询,Post.quer: 如果限制只显示关注用户
的文章,要使用最近添加的User.followed_posts属性,然后将本地变量query中保存的查询进行分页.像往常一样将其传入模板.
'''


@main.route('/', methods=["GET", "POST"])
def index():
    form = PostFrom()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    # 渲染的页数从请求的查询字符串(requset.args)中获取，如果没有明确指定，则默认渲染第一页，参数type=int保证参数无法转换成整数时，返回默认值。
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed'))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)

'''
注意：新文章对象的anthor属性值为表达式current_user.get_current_object()。变量current_user由Flask-Login提供，和所有上下文变量一样，
也是通过线程内的代理对象实现，这个对象的表类似用户对象，但实际上却是一个轻度包装。包含真正的用户对象，数据库需要真实的用户对象，因此要调用
_get_current_object()方法。

这个表单显示在index.html模板中欢迎消息的下方，其后是博客文章列表，在这个博客文章列表中，首次尝试创建博客文章时间轴，按照时间顺序由新到旧
列出数据库中所有的博客文章，对模板所做的改动如下。
'''

# 指向这两个路由的链接添加到模板中,点击这两个链接会为 show_followed cookie 设定适当的值.然后重定向到首页.
# cookie 只能在响应对象中设置,因此这两个路由不能依赖Flask,要使用make_response()方法创建响应对象.

# set-cookie()函数的前两个参数分别是cookie名和值.可选的max_age参数设置cookie的过期时间,单位是秒.如果不指定参数,浏览器关闭后cookie就
# 会过期,本例中,过期时间是三十天.所以即便过几天用户不访问程序,浏览器会记住设定的值.


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', "1", max_age=30*24*60*60)
    return resp


''' 为每个用户创建资料页面, 这个路由在main蓝本中添加,对于名为 john的用户,其资料页面的地址是 http://localhost:5000/user/john.
这个视图函数会在数据库中搜索 URL 指定的用户名,如果找到,则渲染模板user.html,并把用户名作为参数传入模板,如果传入路由的用户名不存在,则返回404错误.
user模板用过渲染保存在用户对象中的信息,这个模板的初始版本:app/templates/user.html
'''


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


# 用户编辑资料的路由

'''
在显示表单之前，视图函数给所有字段设定了初始值。对于给定的字段，这一个工作是通过初始值赋值给form.<field-name>.date完成的。
当form.validate_on_submit()返回False时，表单的三个字段都会使用current_user中保存的初始值。提交表单之后，表单字段的data属性中保存有
更新后的值，因此可以将其赋值给用户对象中的各字段，然后再把用户对象添加到数据库会话中。
为了方便用户能轻易找到编辑页面，可以在资料页面中添加一个链接。>>user.html
'''


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been update')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

# 管理员的资料编辑路由
'''这个路由比较简单，普通用户的编辑路由具有相同基本的结构，在这个视图函数中，用户由id指定，因此可以使用Flask_SQLAlchemy提供的get_or_404
()函数，如果提供的id不正确，则会返回404错误。

用于选择用户角色的SelectFie.设定这个字段的初始值时，role_id被赋值给了field.role.date，这么做的原因在于choices属性中设定的元祖列表使用数字标示符
表示各个选项，表单提交之后，id从字段的data属性中提取，并且查询的时会使用提取出来的id值加载角色对象，表单中声明SelField时使用coerce=int参数，
其作用是保证这个字段的data属性是整数。

为了连接到这个页面，需要在用户资料页面中添加一个链接按钮。'''


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been update')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

'''用户会希望在社交网络中分享某篇文章的链接，为此，每篇文章都需要有一个专门的页面，使用唯一的URL引用，支持固定链接功能的路由和视图函数如下所示，
博客文章的URL使用插入数据库时分配的唯一id字段创建，某些类型的程序会使用可读性高的字符串而不是数字ID构建固定链接。除了数字ID之外，
程序还为了博客文章起了个独特的字符串别名，如程序员问答网站http://stackoverflow.com中的问题链接，采取了问题的英文单词分词进行链接的构建。
可读性和浏览引擎的收录都可以很优。'''


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('You comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

'''
实例化了一个评论表单,并将其传入post.html模板中,以便渲染,提交表单后,插入新评论的逻辑和处理博客文章的过程差不多,和post模型一样,评论的author
字段也不能直接设为current_user,因为这个变量是上下文代理对象,真正的User对象要使用表达式current_user._get_current_object()获取.

评论按照时间戳顺序排列,新评论显示咋爱列表的底部,提交评论后,请求结果是一个重定向,转回之前的URL, 但在url_for()函数的参数中把page设为-1,
这是一个特殊的页数,用于请求评论的最好一页,所以刚才提交的评论才会出现在页面中,程序从查询字符串中获取页数,发现值为-1时, 会计算评论的总量和
总页数,得出真正要显示的页数.

    文章的评论列表通过post.comments 一对多关系获取,按照时间戳顺序进行排列,再使用与博客文章相应的技术进行分页显示,评论列表和分页对象都传入了模板,
以便渲染,FLASKY_COMMENTS_PER_PAGE配置变量也要加入config.py中,用于控制每页显示的评论数量.

评论的渲染过程在新模板_comments.html中进行,类似于_posts.html,但使用的CSS类有所不同,_comments.html模板要引入post.html中,放在文章的正下方,
后面在显示分页导航,可以在git checkout 13a签出对模板进行的改动.
'''

# 视图函数的作用是只允许博客文章的作者编辑文章，但管理员例外，管理员能编辑所有用户的文章，如果用户试图编辑其它用户的文章，视图函数会返回403错误，
# 这个使用的post表单和首页用的是同一个。


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostFrom()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has updated.')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


# 这个视图函数先加载请求的用户,确保用户存在且当前登录用户还没有关注这个用户.然后调用User模型中定义的辅助方法.用于联结两个用户.
# /unfollow/<username>路由的实现方式类似.


@main.route('/folllow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user= User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))

# 用户在其它用户资料页点击关注着数量后,将调用/follower/<username>路由.这个路由的实现如实例所示.

# unfollow路由


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


'''
这个函数加载并验证用户.然后使用十一章介绍的技术,分页展示该用户的followers关系.由于查询关系者返回的是Follow实例列表.为了渲染方便.
将其转换成一个新列表,列表中的各个元素都包含user和timestamp字段.
渲染关注着列表的模板可以写得通用些.以便渲染关注的用户和被关注的用户.模板接收的参数包括用户对象,分页链接使用的端点.分页对象和查询结果列表.
followed_by的端点的实现过程几乎一样.唯一的区别在于,用户列表从user.followed关系中获取.传入模板的参数也要进行相应调整.
'''


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='.followers', pagination=pagination, follows=follows)

#


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page,
                                        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed by',
                           endpoint=".followed_by", pagination=pagination,
                           follows=follows)


'''
在第九章定义了几个用户角色，分别具有不同的权限，其中一个权限是Permission.MODERATE_COMMENTS, 拥有此权限的用户可以管理其他用户的评论。

为了管理评论，要在导航条中添加一个链接，具有权限的用户才可以看到，这个链接在base模板中使用条件语句添加。

管理页面在同一个列表中显示全部文章的评论，最近发表的评论会显示在前面，每篇评论的下方都会显示一个按钮，用来切换disabled属性的值。/moderate
路由的定义如下。
这个函数从数据库读取一页评论，将其传入模板进行渲染，除了评论列表之外，还把分页对象和当前页数传入了模板。
moderate.html模板也是比较简单。因为它依靠之前创建的子模板_comments.html渲染评论。
'''


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

'''
下述启用路由和禁用路由先加载评论对象，把disable字段设为正确的值，再把评论对象写入数据库，最后重定向到评论管理页面，如果查询字符串中指定了
page参数，会将其传入重定向操作。_comments.html 模板中的按钮指定了page参数，重定向会返回之前的页面。
'''


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))





'''
@main.route('/user/<name>')    # 动态路由　name参数动态生成响应
def user(name):
    return render_template('user.html', name=name)   # name=name是关键字参数， 左边的name表示为参数名，就是模板中的占位符
                                                     # 右边的name是当前作用域的变量，表示为同名参数的值。
                                                     # 在模板中使用的{{ name }} 是一种特殊的占位符，告诉模板引擎在这个位置的值从渲染模时的数据获取。

# print app.url_map  可以用这个方法查看URL映射，其中的‘HEAD’, 'OPTIONS', 'GET'是请求方法，Flask指定了请求方法。HEAD和OPTIONS是Flask自动处理的。
'''

'''
这是演示 decorators 装饰器例子的两个页面

在模板中可能也需要检查权限,所以 Permission 类为所有位定义了变量.为了避免每次调用 render_template()时多添加一个参数,
可以使用上下文,上下文处理器能使变量在所有模板中全局可访问.
修改app/main/__init__.py: 把 Permission 类加入模板上下文.

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
'''

# 举两个例子用于使用自定义的修饰器。  权限判断修饰器。


@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return 'For administrators!'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For comment moderators!'


@main.route('/test')
def test_config():
    a = current_app.config['MAIL_USERNAME'] + current_app.config['MAIL_PASSWORD'] +current_app.config['FLASKY_ADMIN']
    return a