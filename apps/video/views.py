import os
from shutil import copyfile

from flask import request, send_file
from flask import Blueprint, g
from werkzeug.utils import secure_filename
from datetime import datetime
from apps.user.verify_token import auth
from config import ALL_METHODS
from .forms import VideoUploadForm, VideoDeleteForm, ImageUploadForm, VideoSaveForm
from ..libs.error_code import NotFound, RequestMethodNotAllowed
from ..libs.restful import params_error, success
from exts import db
from models import Video

video_bp = Blueprint('video', __name__, url_prefix='/video')

basedir = "static/"


@video_bp.route('/upload', methods=ALL_METHODS)
@auth.login_required
def upload_video():
    """
    1.验证POST方法，验证token信息
    2.进行JSON数据格式和表单验证，验证成功后通过g.user获取用户uid,然后像数据库插入数据，
    返回success,否则返回参数错误
    :return: success or params_error
    """
    if request.method != 'POST' and 'content' in request.files:
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoUploadForm()
    if form.validate():
        content = request.files['content']
        uid = g.user.uid
        # 保存视频
        path = basedir + "video/temp"
        filename = secure_filename(content.filename)
        if not filename.endswith('mp4'):
            return params_error(message="文件类型错误")
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + time + "-" + str(uid)
        content.save(os.path.join(path, filename))
        # video = Video(title=title, path=path, uid=uid)
        # db.session.add(video)
        # db.session.commit()
        data = {
            'video': filename
        }
        return success(data=data, message="上传视频成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/cover', methods=ALL_METHODS)
@auth.login_required
def upload_cover():
    if request.method != 'POST' and 'content' in request.files:
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = ImageUploadForm()
    if form.validate():
        content = request.files['content']
        uid = g.user.uid
        # 保存封面
        path = basedir + "image/temp"
        filename = secure_filename(content.filename)
        if not filename.endswith('jpg') and not filename.endswith('png'):
            return params_error(message="文件类型错误")
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + time + "-" + str(uid)
        content.save(os.path.join(path, filename))
        data = {
            'cover': filename
        }
        return success(data=data, message="上传封面成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/save', methods=ALL_METHODS)
@auth.login_required
def save():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoSaveForm()
    if form.validate_for_api() and form.validate():
        title = form.title.data
        video_name = form.video.data
        cover_name = form.cover.data
        uid = g.user.uid
        video_path = basedir + "video/temp/"
        cover_path = basedir + "image/temp/"
        video_path_real = basedir + "video/real/"
        cover_path_real = basedir + "image/cover/"
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        video_name_real = str(uid) + time + ".mp4"
        cover_name_real = str(uid) + time + ".jpg"
        copyfile(video_path + video_name, video_path_real + video_name_real)
        copyfile(cover_path + cover_name, cover_path_real + cover_name_real)
        os.remove(video_path + video_name)
        os.remove(cover_path + cover_name)
        video = Video(title=title, video=video_name_real, cover=cover_name_real, uid=uid)
        db.session.add(video)
        db.session.commit()
        data = {
            'pv': video.id,
            'time': time
        }
        return success(data=data, message="保存视频成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/modify/', methods=ALL_METHODS)
@auth.login_required
def modify():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoUploadForm()
    if form.validate_for_api() and form.validate():
        video_id = form.id.data
        title = form.title.data
        content = request.files['mp4']
        video = db.session.query(Video).filter_by(id=video_id).first()
        if video:
            video.title = title
            video.content = content
            return success(message="修改文章成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route("/delete", methods=ALL_METHODS)
@auth.login_required
def delete():
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoDeleteForm()
    if form.validate_for_api and form.validate():
        video_id = form.pv.data
        video = db.session.query(Video).filter_by(id=video_id).first()
        video_path_real = basedir + "video/real/"
        cover_path_real = basedir + "image/cover/"
        os.remove(video_path_real + video.video)
        os.remove(cover_path_real + video.cover)
        db.session.delete(video)
        db.session.commit()
        return success(message="删除视频成功")
    else:
        return params_error(message=form.get_error())


# @bp.route('/list_all/', methods=ALL_METHODS)
# def list_all():
#
#     if request.method != 'GET':
#         raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
#     dbsession = DBSession.make_session()
#     article_titles = []
#     articles = dbsession.query(Note).filter(Note.id).all()
#     if articles:
#         for article in articles:
#             article_titles.append(article.title)
#     return success(data={"all_articles": article_titles}, message="获取文章列表成功")
#
#
@video_bp.route('/pv<int:id_>/details', methods=ALL_METHODS)
def get_details(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        title = video.title
        likes = video.likes
        collections = video.collections
        coins = video.coins
        data = {
            'title': title,
            'likes': likes,
            'collections': collections,
            "coins": coins
        }
        return success(message="详情", data=data)
    else:
        raise NotFound(msg='未查到视频信息')


@video_bp.route('/pv<int:id_>/video', methods=ALL_METHODS)
def get_video(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        video_path = video.video
        data = {

        }
        return send_file(basedir + "video/real/" + video_path)
        # return success(message="详情", data=data)
    else:
        raise NotFound(msg='未查到视频')


@video_bp.route('/pv<int:id_>/cover', methods=ALL_METHODS)
def get_cover(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        cover_path = video.cover
        data = {

        }
        return send_file(basedir + "image/cover/" + cover_path)
        # return success(message="详情", data=data)
    else:
        raise NotFound(msg='未查到视频')
