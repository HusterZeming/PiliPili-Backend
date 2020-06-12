import os
from shutil import copyfile

from flask import request, send_file
from flask import Blueprint, g, session
from werkzeug.utils import secure_filename
from datetime import datetime
from apps.user.verify_token import auth
from config import ALL_METHODS
from .forms import VideoUploadForm, VideoDeleteForm, ImageUploadForm, VideoSaveForm, VideoPutCoinForm
from ..libs.error_code import NotFound, RequestMethodNotAllowed
from ..libs.restful import params_error, success
from exts import db
from models import Video, User

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
        session['temp_video_name'] = filename
        content.save(os.path.join(path, filename))
        return success(message="上传视频成功")
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
        if filename.endswith('jpg'):
            session['cover_type'] = 'jpg'
        elif filename.endswith('png'):
            session['cover_type'] = 'png'
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + time + "-" + str(uid)
        session['temp_cover_name'] = filename
        content.save(os.path.join(path, filename))
        return success(message="上传封面成功")
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
        video_name = session['temp_video_name']
        cover_name = session['temp_cover_name']
        uid = g.user.uid
        video_path = basedir + "video/temp/"
        cover_path = basedir + "image/temp/"
        video_path_real = basedir + "video/real/"
        cover_path_real = basedir + "image/cover/"
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        video_name_real = str(uid) + "-" + time + ".mp4"
        cover_name_real = str(uid) + "-" + time + session['cover_type']
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


@video_bp.route('/pv<int:id_>/like', methods=ALL_METHODS)
@auth.login_required
def like(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        likes = video.likes
        likes = likes + 1
        video.likes = likes
        db.session.commit()
        data = {
            'likes': likes,
        }
        return success(message="点赞成功", data=data)
    else:
        raise NotFound(msg='未查到视频信息')


@video_bp.route('/pv<int:id_>/put-coin', methods=ALL_METHODS)
@auth.login_required
def put_coin(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoPutCoinForm()
    count = form.coins.data
    user_id = g.user.uid
    user = db.session.query(User).filter_by(id=user_id).first()
    if count <= 0:
        return params_error(message="币数错误")
    if user:
        coins_user = user.coins
        if coins_user < count:
            return params_error(message="币数不够")
        user.coins = coins_user - count
        db.session.commit()
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        coins = video.coins
        coins = coins + count
        video.coins = coins
        uid = video.uid
        db.session.commit()
        user = db.session.query(User).filter_by(id=uid).first()
        if user:
            coins_target = user.coins
            user.coins = coins_target + (count if count < 2 else count / 2)
            db.session.commit()
        data = {
            'coins': coins,
        }
        return success(message="投币成功", data=data)
    else:
        raise NotFound(msg='未查到视频信息')


@video_bp.route('/pv<int:id_>/collect', methods=ALL_METHODS)
@auth.login_required
def collect(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        collections = video.collections
        collections = collections + 1
        video.likes = collections
        pv = video.id
        db.session.commit()
        data = {
            'collections': collections,
            'pv': pv
        }
        return success(message="收藏成功", data=data)
    else:
        raise NotFound(msg='未查到视频信息')


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
        views = video.views
        data = {
            'title': title,
            'likes': likes,
            'collections': collections,
            'coins': coins,
            'views': views
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
        views = video.views
        video.views = views + 1
        db.session.commit()
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
