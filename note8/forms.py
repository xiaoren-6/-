from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.validators import Email, EqualTo
from mysql_utils import MysqlUtils
from wtforms import Form, PasswordField, validators
from wtforms import Form, PasswordField, StringField, validators


# 登录表单
class LoginForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=2, max=20, message="长度在2-20个字符之间")
        ]

    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message="长度在6-20个字符之间")
        ]
    )

    def validate_username(self, field):
        # 根据用户名查找users表中记录
        sql = "SELECT *  FROM users WHERE username='%s'" % (field.data)
        db = MysqlUtils()  # 实例化数据库操作类
        result = db.fetchone(sql)  # 获取一条记录
        if not result:
            raise ValidationError("用户名不存在")


# 注册表单
class RegisterForm(Form):
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=2, max=20, message="长度在2-20个字符之间")
        ]
    )
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入邮箱'),
            Email(message="请输入正确的邮箱格式")
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20, message="长度在6-20个字符之间")
        ]
    )
    confirm = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20),
            EqualTo('password', message='2次输入密码不一致')
        ]
    )


# 文章表单
class ArticleForm(Form):
    title = StringField(
        '标题',
        validators=[
            DataRequired(message='长度在2-30个字符'),
            Length(min=2, max=30)
        ]
    )

    content = TextAreaField(
        '内容',
        validators=[
            DataRequired(message='长度不少于5个字符'),
            Length(min=5)
        ]
    )


# 修改密码表单
class ChangePasswordForm(Form):
    old_password = PasswordField(
        '旧密码',
        validators=[
            DataRequired(message='旧密码不能为空'),
            Length(min=6, max=20, message="长度在6-20个字符之间")
        ]
    )
    new_password = PasswordField(
        '新密码',
        validators=[
            DataRequired(message='新密码不能为空'),
            Length(min=6, max=20, message="长度在6-20个字符之间")
        ]
    )
    confirm = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, max=20),
            EqualTo('new_password', message='2次输入密码不一致')
        ]
    )


