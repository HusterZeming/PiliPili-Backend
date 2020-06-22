from flask import request
from flask import Blueprint, g
from apps.user.verify_token import auth
from config import ALL_METHODS
from ..libs.error_code import RequestMethodNotAllowed
from ..libs.restful import params_error, success, unauthorized_error
from exts import db
from models import Video, Danmuku

danmuku_bp = Blueprint('danmuku', __name__, url_prefix='/danmuku')


@danmuku_bp.route("/danmuku<int:id_>/delete", methods=ALL_METHODS)
@auth.login_required
def delete(id_):
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    danmuku = db.session.query(Danmuku).filter_by(id=id_).first()
    user_id = g.user.uid
    if not user_id == danmuku.uid:
        return unauthorized_error(message="没有权限")
    video = db.session.query(Video).filter_by(id=danmuku.target).first()
    if video:
        video.danmuku = video.danmuku - 1 if video.danmuku else 0
    db.session.delete(danmuku)
    db.session.commit()
    return success(message="删除弹幕成功")


@danmuku_bp.route("/danmuku<int:id_>/details", methods=ALL_METHODS)
def details(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    danmuku = db.session.query(Danmuku).filter_by(id=id_).first()
    if danmuku:
        data = {
            'id': danmuku.id,
            'content': danmuku.content,
            'time': danmuku.time,
            'type': danmuku.type,
            'color': danmuku.color,
            'size': danmuku.size,
            'background': danmuku.background,
            'author': danmuku.uid
        }
        return success(data=data, message="获取弹幕成功")
    else:
        return params_error(message="未查到弹幕")
