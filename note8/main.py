import time
from flask import Flask
from flask import request, redirect, url_for, flash, session, render_template
from passlib.hash import sha256_crypt
from forms import LoginForm, RegisterForm, ArticleForm, ChangePasswordForm
from mysql_utils import MysqlUtils

app = Flask(__name__)
app.secret_key = 'gec123'
app.config['SECRET_KEY'] = 'gec121'


# 首页 暂时没有写完整！！！！！！

@app.route('/')
def index():
    count = 3  # 每页显示数量
    page = request.args.get('page')  # 获取当前的页码
    if page is None:  # 默认设置页码为1
        page = 1
    # 从articles表中,假设是刷选出5条数据，并根据日期降序排序
    sql = f'SELECT * FROM articles ORDER BY create_date DESC LIMIT {(int(page) - 1) * count},{count}'
    db = MysqlUtils()
    articles = db.fetchall(sql)  # 获取多条记录
    # 渲染模板
    return render_template('home.html', articles=articles, page=int(page))


# 关于
@app.route('/about')
def about_page():
    return render_template('about.html')


# 在其他地方构建 URL 时，使用新的端点名称 'about_page'
# 例如: url_for('about_page') 或 redirect(url_for('about_page'))

# 个人中心
@app.route('/people')
def people_page():
    return render_template('people.html')


# 在其他地方构建 URL 时，使用新的端点名称 'people_page'
# 例如: url_for('people_page') 或 redirect(url_for('people_page'))


# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)  # 实例化表单类
    # 如果提交表单，请求方法为POST，并且字段验证通过
    if request.method == 'POST' and form.validate():
        # 获取字段内容
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # 保存数据，实例化数据库操作类
        db = MysqlUtils()
        # 向users表中插入数据
        sql = "INSERT INTO users(email,username, password)VALUES('%s','%s','%s')" % (email, username, password)
        db.insert(sql)
        flash("您已注册成功,请先登录", "success")  # 消息闪现
        return redirect(url_for('login'))  # 跳转到登录页面
    return render_template('register.html', form=form)

# 修改密码
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm(request.form)

    if 'username' not in session:
        flash("请先登录！", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST' and form.validate():
        old_password = form.old_password.data
        new_password = form.new_password.data

        db = MysqlUtils()
        # 使用参数化查询来防止SQL注入
        sql = "SELECT * FROM users WHERE username=%s"
        result = db.fetchone(sql, (session['username'],))

        if result is None:
            flash("未找到用户！", "danger")
            return redirect(url_for('login'))

        password_hash = result['password']

        # 使用相同的加密方式来验证旧密码
        if sha256_crypt.verify(old_password, password_hash):
            # 存储新密码时使用加密
            encrypted_new_password = sha256_crypt.encrypt(str(new_password))
            # 使用参数化查询来更新密码
            update_sql = "UPDATE users SET password=%s WHERE username=%s"
            db.update(update_sql, (encrypted_new_password, session['username'])) # 使用update方法
            # 确保提交更改，注意：update方法已经包含了提交的逻辑，所以这里不需要再次调用db.commit()
            flash("密码修改成功！", "success")
            return redirect(url_for('index'))
        else:
            flash("原密码错误，请重新输入！", "danger")

    return render_template('change_password.html', form=form)

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已经登录，则直接跳转到首页（或者控制台）
    if "logged_in" in session:
        return redirect(url_for('index'))
        # return redirect(url_for('dashboard'))
    # 实例化表单
    form = LoginForm(request.form)
    # 如果提交表单，并字段验证通过
    if form.validate_on_submit():
        # 从表单中获取字段
        username = request.form['username']
        password_user = request.form['password']
        # 查询数据
        sql = "SELECT * FROM users WHERE username='%s'" % (username)
        # 实例化数据库操作类
        db = MysqlUtils()
        result = db.fetchone(sql)  # 获取一条记录
        password = result['password']
        # 对比用户填写的密码和数据库中的记录密码是否一致,如果为真，验证通过
        if sha256_crypt.verify(password_user, password):
            # 写入session
            session['logged_in'] = True
            session['username'] = username
            flash("登录成功！", "success")  # 消息闪现
            return redirect(url_for('index'))  # 直接跳转到首页（或者控制台）
            # return redirect(url_for('dashboard'))  # 直接跳转到首页（或者控制台）
        else:  # 如果密码错误
            flash("用户名和密码不匹配！", "danger")
    return render_template('login.html', form=form)


# 如果用户已经登录
def is_logged_in(fun):
    def warp(*args, **kwargs):
        if 'logged_in' in session:  # 判断是否登录
            # 如果登录，继续执行被装饰的函数
            return fun(*args, **kwargs)
        else:
            # 如果没有登录，提示无权访问
            flash("无权访问,请先登录!", "danger")
            return redirect(url_for('login'))

    return warp


# 退出
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("您已成功退出!", "success")
    return redirect(url_for('login'))


# 控制台
@app.route('/dashboard')
def dashboard():
    db = MysqlUtils()
    sql = "SELECT * FROM articles WHERE author='%s' ORDER BY create_date DESC" % (session['username'])
    # 根据用户名查找用户笔记信息
    result = db.fetchall(sql)
    if result:  # 如果笔记存在，赋值给articles变量
        return render_template('dashboard.html', articles=result)
    else:
        msg = "暂无笔记信息"
        return render_template('dashboard.html', msg=msg)


@app.route('/add_article', methods=["GET", "POST"])
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        # 获取表单内容
        title = form.title.data
        content = form.content.data
        author = session['username']
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db = MysqlUtils()
        sql = "INSERT INTO articles(title,content,author,create_date)VALUES('%s','%s','%s','%s')" % (
            title, content, author, create_date)
        db.insert(sql)
        flash("创建成功", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


# 删除笔记
@app.route('/delete_article/<string:id>', methods=["POST"])
def delete_article(id):
    db = MysqlUtils()
    sql = "DELETE FROM articles WHERE id='%s' and author='%s'" % (id, session['username'])
    db.delete(sql)  # 删除数据库中的数据
    flash("删除成功!", "success")
    return redirect(url_for('dashboard'))  # 跳转回控制台界面


# 编辑笔记
@app.route('/edit_article/<string:id>', methods=["GET", "POST"])
def edit_article(id):
    db = MysqlUtils()
    # 根据笔记id,作者查询笔记信息
    fetch_sql = "SELECT * FROM articles WHERE id='%s'and author='%s'" % (id, session['username'])
    article = db.fetchone(fetch_sql)  # 查询一条记录
    # 检测笔记不存在的情况
    if not article:
        flash("ID错误", "danger")
        return redirect(url_for('dashboard'))
    # 获取表单
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        # 获取表单内容
        title = request.form['title']
        content = request.form['content']
        update_sql = "UPDATE articles SET title='%s',content='%s'WHERE id='%s' and author='%s'" % (
            title, content, id, session['username'])
        db = MysqlUtils()
        db.update(update_sql)
        flash('更新成功!', "success")
        return redirect(url_for('dashboard'))
    # 重新从数据库中获取表单字段的值
    form.title.data = article['title']
    form.content.data = article['content']
    return render_template('edit_article.html', form=form)


# 笔记详情
@app.route('/article/<string:id>')
def article(id):
    db = MysqlUtils()
    # 根据笔记id查询笔记信息
    fetch_sql = "SELECT * FROM articles WHERE id='%s'" % id
    article = db.fetchone(fetch_sql)
    if not article:
        flash("笔记不存在", "danger")
        return redirect(url_for('dashboard'))
    return render_template('article.html', article=article)


# 定义 404 错误处理函数
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=8900)
