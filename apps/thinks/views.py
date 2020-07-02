from datetime import datetime

from flask import request
from flask import Blueprint, g
from apps.user.verify_token import auth
from config import ALL_METHODS, bucket
from .forms import ThinkUploadForm, ThinkUploadPhotoForm
from ..libs.bucket_get_token import get_bucket_token
from ..libs.error_code import RequestMethodNotAllowed
from ..libs.restful import params_error, success, unauthorized_error
from exts import db
from models import User, Think, Video

think_bp = Blueprint('think', __name__, url_prefix='/think')


@think_bp.route('/photo', methods=ALL_METHODS)
@auth.login_required
def upload_cover_new():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = ThinkUploadPhotoForm()
    if form.validate_for_api() and form.validate():
        uid = g.user.uid
        user = db.session.query(User).filter_by(id=uid).first()
        if user.cover_name_temp:
            bucket.delete_object(user.cover_name_temp)
        filename = form.filename.data
        if not filename.endswith('jpg') and not filename.endswith('png'):
            return params_error(message="文件类型错误")
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = 'uid-' + str(uid) + '-' + time + '-' + filename
        user.cover_name_temp = filename
        db.session.commit()
        data = get_bucket_token(filename)
        return success(message="上传图片成功", data=data)
    else:
        return params_error(message=form.get_error())


@think_bp.route('/post', methods=ALL_METHODS)
@auth.login_required
def post():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = ThinkUploadForm()
    if form.validate_for_api() and form.validate():
        content = form.content.data
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        is_video = False
        if form.video.data:
            video = db.session.query(Video).filter_by(id=form.video.data).first()
            photo = video.cover
            is_video = True
        else:
            photo = user.think_name_temp
            is_video = False
        think = Think(content=content, photo=photo, uid=user.id, is_video=is_video)
        db.session.add(think)
        db.session.commit()
        user.think_name_temp = ''
        db.session.commit()
        return success(message="发布成功")
    else:
        return params_error(message=form.get_error())


@think_bp.route('/think<int:id_>/delete', methods=ALL_METHODS)
@auth.login_required
def delete(id_):
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=g.user.uid).first()
    think = db.session.query(Think).filter_by(id=id_).first()
    if think.uid != user.id:
        return unauthorized_error(message="没有权限")
    if not think.is_video and think.photo:
        bucket.delete_object(think.photo)
    db.session.delete(think)
    db.session.commit()
    return success(message="删除成功")


@think_bp.route('/uid<int:id_>/get-all-thinks', methods=ALL_METHODS)
@auth.login_required
def get_all_thinks(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    user = db.session.query(User).filter_by(id=g.user.uid).first()
    list_ = []
    if not user.followings:
        data = {
            'list': list_
        }
    else:
        all_followings = list(map(int, user.followings.split(',')))
        for followings_id in all_followings:
            following = db.session.query(User).filter_by(id=followings_id).first()
            thinks = db.session.query(Think).filter(Think.uid == following.id).all()
            for think_item in thinks:
                think = {
                    'id': think_item.id,
                    'content': think_item.content,
                    'photo': think_item.photo,
                    'author': following.id,
                    'author_name': following.username,
                    'bucket_photo': get_bucket_token(think_item.photo),
                    'bucket_avatar': get_bucket_token(following.avatar),
                    'time': think_item.upload_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                list_.append(think)
        data = {
            'list': list_
        }
    return success(message="获取成功", data=data)

