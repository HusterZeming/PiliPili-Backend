from flask import Blueprint, request

from .generate_token import generate_token
from .forms import RegisterForm, LoginForm
from models import User
from apps.libs.restful import unauthorized_error, params_error, success
from apps.libs.error_code import RequestMethodNotAllowed
from config import ALL_METHODS
from .verify_token import auth
from exts import db

# 用户蓝图，访问需加前缀/user
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/login', methods=ALL_METHODS)
def login():
    # 登录
    print(request.method)
    # 验证Request method是否为POST,如果不是抛出405
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = LoginForm()
    # 检查表单
    if request.method == 'POST' and form.validate_for_api() and form.validate():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if not user or not user.check_password(form.password.data):
            return unauthorized_error(message="邮箱或密码错误")
        # 生成token
        token = generate_token(user.id)
        result = {
            'username': user.username,
            'token': token.decode('ascii')
        }
        return success(data=result, message="登录成功")
    return params_error(message=form.get_error())


@user_bp.route('/register', methods=ALL_METHODS)
def register():
    # 注册
    print(request.method)
    # 验证Request method是否为POST,如果不是抛出405
    if request.method.upper() != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    # dbsession = DBSession.make_session()
    form = RegisterForm()
    if form.validate_for_api() and form.validate():
        if form.validate_email(form.email):
            email = form.email.data
            password = form.password.data
            username = form.username.data
            user = User(email=email, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return success(message="注册成功")
    return params_error(message=form.get_error())


# 验证token
@user_bp.route('/verify', methods=ALL_METHODS)
@auth.login_required()
def verify_token():
    return success(message="有效")
