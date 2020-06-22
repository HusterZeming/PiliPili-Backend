from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import Email, InputRequired, Length
from base_form import BaseForm, UploadBaseForm
from flask_wtf.file import FileField, FileAllowed
from models import User
from apps.libs.error_code import ParameterException


class LoginForm(BaseForm):
    # 登录
    email = StringField(
        validators=[Email(message="请输入正确的邮箱"), Length(6, 50, message="email"), InputRequired(message="请输入邮箱")])
    password = StringField(validators=[Length(6, 20, message="密码长度6位到20位"), InputRequired("请输入密码")])


def validate_username(username):
    if User.query.filter_by(username=username.data).first():
        raise ParameterException(msg="用户名已被占有")
    return True


def validate_email(email):
    if User.query.filter_by(email=email.data).first():
        raise ParameterException(msg="邮箱已经被注册")
    return True


class RegisterForm(BaseForm):
    # 注册
    email = StringField(validators=[Length(6, 25, message="邮箱长度6位到25位"), Email(message="请输入正确的邮箱")])
    password = StringField(validators=[Length(6, 20, message="请正确输入密码")])
    username = StringField([InputRequired(message="请输入用户名"), Length(2, 15, message="用户名位2到15个字符")])


class UserPutCoinForm(BaseForm):
    coins = IntegerField(validators=[InputRequired(message="请输入投币个数")])


class UserPutUsernameForm(BaseForm):
    username = StringField([InputRequired(message="请输入用户名"), Length(2, 15, message="用户名位2到15个字符")])
    cost = IntegerField(validators=[InputRequired(message="请输入花费币个数")])


class UserFanForm(BaseForm):
    id = IntegerField(validators=[InputRequired(message="请输入用户id")])


class UserPutSignForm(BaseForm):
    sign = StringField(validators=[Length(0, 70, message="签名最多70个字符")])


class UserPutGenderForm(BaseForm):
    gender = BooleanField()


class UserPutVipForm(BaseForm):
    vip = IntegerField(validators=[InputRequired(message="请输入vip持续天数")])
    coins = IntegerField(validators=[InputRequired(message="请输入所扣P币")])


class UserGetFanForm(BaseForm):
    id = IntegerField(validators=[InputRequired(message="请输入用户id")])
    page_count = IntegerField(validators=[InputRequired(message="请输入页面容量")])
    page = IntegerField(validators=[InputRequired(message="请输入页号")])


class ImageUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('jpg', 'png')])
