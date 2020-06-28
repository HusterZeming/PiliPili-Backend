import datetime
import os
from flask import Blueprint, request
from werkzeug.security import generate_password_hash

from .generate_token import generate_token
from .forms import RegisterForm, LoginForm, UserPutCoinForm, UserFanForm, UserGetFanForm, UserPutUsernameForm, \
    validate_email, validate_username, ImageUploadForm, UserPutSignForm, UserPutGenderForm, UserPutVipForm, \
    PutPasswordForm
from models import User, Video
from apps.libs.restful import unauthorized_error, params_error, success
from apps.libs.error_code import RequestMethodNotAllowed
from config import ALL_METHODS
from .verify_token import auth
from werkzeug.utils import secure_filename
from flask import g
from exts import db
from config import bucket

# 用户蓝图，访问需加前缀/user
from apps.libs.bucket_get_token import get_bucket_token

user_bp = Blueprint('user', __name__, url_prefix='/user')

basedir = "static/"


@user_bp.route('/login', methods=ALL_METHODS)
def login():
    # 登录
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
    # 验证Request method是否为POST,如果不是抛出405
    if request.method.upper() != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = RegisterForm()
    if form.validate_for_api() and form.validate():
        if validate_email(form.email) and validate_username(form.username):
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


@user_bp.route('/details', methods=ALL_METHODS)
@auth.login_required
def details():
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user_id = g.user.uid
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'gender': user.gender,
            'coins': user.coins,
            'vip': user.vip_end,
            'fans_count': len(list(map(int, user.fans.split(',')))) if user.fans else 0,
            'followings_count': len(list(map(int, user.followings.split(',')))) if user.followings else 0
        }
        return success(message="获取用户信息成功", data=data)
    else:
        return params_error(message='未查到用户信息')


@user_bp.route('/put-coin', methods=ALL_METHODS)
@auth.login_required
def put_coin():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserPutCoinForm()
    if form.validate_for_api() and form.validate():
        count = form.coins.data
        user_id = g.user.uid
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            coins = user.coins
            if count <= 0:
                return params_error(message="币数错误")
            user.coins = coins + count
            db.session.commit()
            data = {
                'coins': coins + count,
            }
            return success(message="购买P币成功", data=data)
    else:
        return params_error(message=form.get_error())


@user_bp.route('/put-username', methods=ALL_METHODS)
@auth.login_required
def put_username():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserPutUsernameForm()
    if form.validate_for_api() and form.validate():
        if validate_username(form.username):
            username = form.username.data
            cost = form.cost.data
            if cost < 0:
                return params_error(message="币数错误")
            user_id = g.user.uid
            user = db.session.query(User).filter_by(id=user_id).first()
            if user:
                user.username = username
                if cost > user.coins:
                    return params_error(message="币数不足")
                user.coins = user.coins - cost
                db.session.commit()
            data = {
                'username': username,
                'coins': user.coins
            }
            return success(message="改名成功", data=data)
    else:
        return params_error(message=form.get_error())


@user_bp.route('/uid<int:id_>/details', methods=ALL_METHODS)
def open_details(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=id_).first()
    if user:
        all_video = db.session.query(Video).filter_by(uid=id_).all()
        likes = 0
        if all_video:
            for video in all_video:
                likes += len(list(map(int, video.likes_user.split(',')))) if video.likes_user else 0
        data = {
            'id': user.id,
            'username': user.username,
            'gender': user.gender,
            'vip': user.vip_end,
            'sign': user.sign,
            'likes': likes,
            'fans_count': len(list(map(int, user.fans.split(',')))) if user.fans else 0,
            'followings_count': len(list(map(int, user.followings.split(',')))) if user.followings else 0
        }
        return success(message="获取用户信息成功", data=data)
    else:
        return params_error(message="未查到用户信息")


@user_bp.route('/fan', methods=ALL_METHODS)
@auth.login_required
def fan():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserFanForm()
    if form.validate_for_api() and form.validate():
        target_id = form.id.data
        user_id = g.user.uid
        if user_id == target_id:
            return params_error(message="无法关注自己")
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            if user.followings:
                followings = list(map(int, user.followings.split(',')))
                if target_id in followings:
                    return params_error(message="已粉")
                followings.append(target_id)
                user.followings = ','.join(str(i) for i in followings)
                db.session.commit()
            else:
                followings = [target_id]
                user.followings = followings
                db.session.commit()
            target_user = db.session.query(User).filter_by(id=target_id).first()
            if target_user.fans:
                fans = list(map(int, target_user.fans.split(',')))
                if user_id not in fans:
                    fans.append(user_id)
                    target_user.fans = ','.join(str(i) for i in fans)
                    db.session.commit()
                else:
                    return params_error(message="已是粉丝")
            else:
                fans = [user_id]
                target_user.fans = fans
                db.session.commit()
            data = {
                'fans_count': len(list(map(int, target_user.fans.split(','))))
            }
            return success(message="已关注", data=data)
    else:
        return params_error(message=form.get_error())


@user_bp.route('/un-fan', methods=ALL_METHODS)
@auth.login_required
def un_fan():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserFanForm()
    if form.validate_for_api() and form.validate():
        target_id = form.id.data
        user_id = g.user.uid
        if user_id == target_id:
            return params_error(message="无法取关自己")
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            followings = list(map(int, user.followings.split(',')))
            if not followings:
                return params_error(message="关注数为0")
            if target_id not in followings:
                return params_error(message="未粉")
            followings.remove(target_id)
            if followings:
                user.followings = ','.join(str(i) for i in followings)
            else:
                user.followings = None
            db.session.commit()
            target_user = db.session.query(User).filter_by(id=target_id).first()
            fans = list(map(int, target_user.fans.split(',')))
            if not fans:
                return params_error(message="粉丝数为0")
            if user_id not in fans:
                return params_error(message="不是粉丝")
            fans.remove(user_id)
            if followings:
                target_user.fans = ','.join(str(i) for i in fans)
            else:
                target_user.fans = None
            db.session.commit()
            data = {
                'fans_count': len(list(map(int, target_user.fans.split(',')))) if target_user.fans else 0,
            }
            return success(message="取消关注", data=data)
    else:
        return params_error(message=form.get_error())


@user_bp.route('/get-fans', methods=ALL_METHODS)
def get_fans():
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserGetFanForm()
    if form.validate_for_api() and form.validate():
        user_id = form.id.data
        page = form.page.data
        page_count = form.page_count
        start = (page - 1) * page_count
        end = start + page_count
        fans = []
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            if not user.fans:
                data = {
                    'fans': ''
                }
            else:
                all_fans = list(map(int, user.fans.split(',')))
                for i in range(start, end):
                    if i < len(all_fans):
                        fans.append(all_fans[i])
                    else:
                        break
                data = {
                    'fans': fans
                }
            return success(message="获取成功", data=data)
    else:
        return params_error(message=form.get_error())


@user_bp.route('/upload-avatar', methods=ALL_METHODS)
@auth.login_required
def upload_avatar():
    if request.method != 'POST' and 'content' in request.files:
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = ImageUploadForm()
    if form.validate():
        content = request.files['content']
        uid = g.user.uid
        filename = secure_filename(content.filename)
        path = basedir + "image/temp"
        user = db.session.query(User).filter_by(id=uid).first()
        if user.avatar:
            bucket.delete_object(user.avatar)
        time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if filename.endswith('jpg'):
            avatar_name = str(uid) + '-' + time + '-avatar.jpg'
        elif filename.endswith('png'):
            avatar_name = str(uid) + '-' + time + '-avatar.png'
        else:
            return params_error(message="文件类型错误")
        filename = filename + time + "-" + str(uid)
        content.save(os.path.join(path, filename))
        bucket.put_object_from_file(avatar_name, path + '/' + filename)
        user = db.session.query(User).filter_by(id=uid).first()
        user.avatar = avatar_name
        db.session.commit()
        os.remove(path + '/' + filename)
        data = {
            'avatar': avatar_name
        }
        return success(data=data, message="上传头像成功")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/upload-background', methods=ALL_METHODS)
@auth.login_required
def upload_background():
    if request.method != 'POST' and 'content' in request.files:
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = ImageUploadForm()
    if form.validate():
        content = request.files['content']
        uid = g.user.uid
        filename = secure_filename(content.filename)
        path = basedir + "image/temp"
        user = db.session.query(User).filter_by(id=uid).first()
        if user.background:
            bucket.delete_object(user.background)
        time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if filename.endswith('jpg'):
            background_name = str(uid) + '-' + time + '-background.jpg'
        elif filename.endswith('png'):
            background_name = str(uid) + '-' + time + '-background.png'
        else:
            return params_error(message="文件类型错误")
        filename = filename + time + "-" + str(uid)
        content.save(os.path.join(path, filename))
        bucket.put_object_from_file(background_name, path + '/' + filename)
        user.background = background_name
        db.session.commit()
        os.remove(path + '/' + filename)
        data = {
            'background': background_name
        }
        return success(data=data, message="上传背景成功")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/uid<int:id_>/get-avatar', methods=ALL_METHODS)
def get_avatar(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=id_).first()
    if user:
        avatar_path = user.avatar
        return success(message="头像", data=get_bucket_token(avatar_path))
    else:
        return params_error(message="未查到用户头像")


@user_bp.route('/uid<int:id_>/get-background', methods=ALL_METHODS)
def get_background(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=id_).first()
    if user:
        background_path = user.background
        return success(message="背景", data=get_bucket_token(background_path))
    else:
        return params_error(message="未查到用户背景")


@user_bp.route('/upload-sign', methods=ALL_METHODS)
@auth.login_required
def upload_sign():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserPutSignForm()
    if form.validate_for_api and form.validate():
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if user:
            user.sign = form.sign.data
            db.session.commit()
            data = {
                'sign': user.sign
            }
            return success(message="签名", data=data)
        else:
            return params_error(message="未查到用户")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/put-gender', methods=ALL_METHODS)
@auth.login_required
def put_gender():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserPutGenderForm()
    if form.validate_for_api and form.validate():
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if user:
            gender = form.gender.data
            user.gender = gender
            db.session.commit()
            data = {
                'gender': user.gender
            }
            return success(message="性别", data=data)
        else:
            return params_error(message="未查到用户")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/get-space', methods=ALL_METHODS)
@auth.login_required
def get_space():
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=g.user.uid).first()
    if user:
        all_video = db.session.query(Video).filter_by(uid=g.user.uid).all()
        likes = 0
        if all_video:
            for video in all_video:
                likes += len(list(map(int, video.likes_user.split(',')))) if video.likes_user else 0
        data = {
            'sign': user.sign if user.sign else '这个人很懒，什么都没有留下',
            'likes': likes
        }
        return success(message="空间数据", data=data)
    else:
        return params_error(message="未查到用户")


@user_bp.route('/put-vip', methods=ALL_METHODS)
@auth.login_required
def put_vip():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = UserPutVipForm()
    if form.validate_for_api() and form.validate():
        vip = form.vip.data
        if vip <= 0:
            return params_error(message="vip天数需大于0")
        coins = form.coins.data
        if coins <= 0:
            return params_error(message="P币数需大于0")
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if user:
            if coins > user.coins:
                return params_error(message="用户P币数不够")
            user.coins -= coins
            user.vip += vip
            user.vip_end = (datetime.datetime.now() + datetime.timedelta(days=user.vip)).strftime('%Y-%m-%d')
            db.session.commit()
            data = {
                'vip': user.vip_end,
                'coins': user.coins
            }
            return success(message="购买大会员成功", data=data)
        else:
            return params_error(message="未查到用户")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/check-password', methods=ALL_METHODS)
@auth.login_required
def check_password():
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = PutPasswordForm()
    if form.validate_for_api() and form.validate():
        password = form.password.data
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if user:
            if user.check_password(password):
                return success(message="密码正确")
            else:
                return params_error(message="密码错误")
        else:
            return params_error(message="未查到用户")
    else:
        return params_error(message=form.get_error())


@user_bp.route('/put-password', methods=ALL_METHODS)
@auth.login_required
def put_password():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = PutPasswordForm()
    if form.validate_for_api() and form.validate():
        password = form.password.data
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if user:
            user._password = generate_password_hash(password)
            db.session.commit()
            return success(message="修改成功")
        else:
            return params_error(message="未查到用户")
    else:
        return params_error(message=form.get_error())


@user_bp.route("/uid<int:id_>/get-video", methods=ALL_METHODS)
def get_video(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    all_video = db.session.query(Video).filter_by(uid=id_).all()
    video_list = []
    if all_video:
        for video in all_video:
            video_list.append(video.id)
    data = {
         'video_list': video_list
    }
    return success(data=data, message="获取投稿成功")
