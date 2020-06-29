import os
import random
from config import bucket
from flask import request
from flask import Blueprint, g, session
from werkzeug.utils import secure_filename
from datetime import datetime
from apps.user.verify_token import auth
from config import ALL_METHODS
from .forms import VideoUploadForm, ImageUploadForm, VideoSaveForm, VideoPutCoinForm, \
    VideoPutCommentForm, VideoPutDanmukuForm, VideoNewUploadForm, VideoNewCancelForm
from apps.libs.bucket_get_token import get_bucket_token
from ..libs.error_code import RequestMethodNotAllowed
from ..libs.restful import params_error, success, unauthorized_error
from exts import db
from moviepy.editor import VideoFileClip
from models import Video, User, Comment, Danmuku

video_bp = Blueprint('video', __name__, url_prefix='/video')

basedir = "static/"


@video_bp.route('/upload', methods=ALL_METHODS)
@auth.login_required
def upload_video():
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


@video_bp.route('/upload-new', methods=ALL_METHODS)
@auth.login_required
def upload_video_new():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoNewUploadForm()
    if form.validate_for_api() and form.validate():
        uid = g.user.uid
        user = db.session.query(User).filter_by(id=uid).first()
        if user.video_name_temp:
            bucket.delete_object(user.video_name_temp)
        # 保存视频
        filename = form.filename.data
        if not filename.endswith('mp4') and not filename.endswith('mpeg'):
            return params_error(message="文件类型错误")
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = 'uid-' + str(uid) + '-' + time + '-' + filename
        user.video_name_temp = filename
        db.session.commit()
        data = get_bucket_token(filename)
        return success(message="上传视频成功", data=data)
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
            session['cover_type'] = '.jpg'
        elif filename.endswith('png'):
            session['cover_type'] = '.png'
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = filename + time + "-" + str(uid)
        session['temp_cover_name'] = filename
        content.save(os.path.join(path, filename))
        return success(message="上传封面成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/cover-new', methods=ALL_METHODS)
@auth.login_required
def upload_cover_new():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoNewUploadForm()
    if form.validate_for_api() and form.validate():
        uid = g.user.uid
        user = db.session.query(User).filter_by(id=uid).first()
        if user.cover_name_temp:
            bucket.delete_object(user.cover_name_temp)
        # 保存视频
        filename = form.filename.data
        if not filename.endswith('jpg') and not filename.endswith('png'):
            return params_error(message="文件类型错误")
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = 'uid-' + str(uid) + '-' + time + '-' + filename
        user.cover_name_temp = filename
        db.session.commit()
        data = get_bucket_token(filename)
        return success(message="上传封面成功", data=data)
    else:
        return params_error(message=form.get_error())


@video_bp.route('/save', methods=ALL_METHODS)
@auth.login_required
def save():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoSaveForm()
    if form.validate_for_api() and form.validate():
        video_path = basedir + "video/temp/"
        cover_path = basedir + "image/temp/"
        uid = g.user.uid
        keys = session.keys()
        if 'temp_video_name' not in keys or 'temp_cover_name' not in keys or 'cover_type' not in keys:
            for file in os.listdir(video_path):
                if file.endswith(str(uid)):
                    os.remove(video_path + file)
            for file in os.listdir(cover_path):
                if file.endswith(str(uid)):
                    os.remove(cover_path + file)
            return params_error(message="cookie错误")
        title = form.title.data
        sign = form.sign.data
        type = form.type.data
        video_name = session['temp_video_name']
        cover_name = session['temp_cover_name']
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        cover_type = session['cover_type']
        video_name_real = str(uid) + "-" + time + ".mp4"
        cover_name_real = str(uid) + "-" + time + cover_type
        os.rename(video_path + video_name, video_path + video_name_real)
        os.rename(cover_path + cover_name, cover_path + cover_name_real)
        clip = VideoFileClip(video_path + video_name_real)
        bucket.put_object_from_file(video_name_real, video_path + video_name_real)
        bucket.put_object_from_file(cover_name_real, cover_path + cover_name_real)
        video = Video(title=title, video=video_name_real, cover=cover_name_real, sign=sign, duration=clip.duration,
                      type=type, uid=uid)
        clip.close()
        db.session.add(video)
        db.session.commit()
        data = {
            'pv': video.id,
            'time': time
        }
        os.remove(video_path + video_name_real)
        os.remove(cover_path + cover_name_real)
        return success(data=data, message="保存视频成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/save-new', methods=ALL_METHODS)
@auth.login_required
def save_new():
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoSaveForm()
    user = db.session.query(User).filter_by(id=g.user.uid).first()
    # if not user.cover_name_temp or not user.video_name_temp:
    #     return params_error(message="未上传视频或封面")
    if form.validate_for_api() and form.validate():
        title = form.title.data
        sign = form.sign.data
        duration = form.duration.data
        type = form.type.data
        video = Video(title=title, video=user.video_name_temp, cover=user.cover_name_temp, sign=sign, duration=duration,
                      type=type, uid=user.id)
        db.session.add(video)
        db.session.commit()
        user.video_name_temp = ""
        user.cover_name_temp = ""
        db.session.commit()
        return success(message="保存视频成功")
    else:
        return params_error(message=form.get_error())


@video_bp.route('/cancel', methods=ALL_METHODS)
@auth.login_required
def cancel():
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    uid = g.user.uid
    video_path = basedir + "video/temp/"
    cover_path = basedir + "image/temp/"
    for file in os.listdir(video_path):
        if file.endswith(str(uid)):
            os.remove(video_path + file)
    for file in os.listdir(cover_path):
        if file.endswith(str(uid)):
            os.remove(cover_path + file)
    return success(message="取消成功")


@video_bp.route('/cancel-new', methods=ALL_METHODS)
@auth.login_required
def cancel_new():
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    form = VideoNewCancelForm()
    if form.validate_for_api() and form.validate():
        goto_bucket = form.goto_bucket.data
        user = db.session.query(User).filter_by(id=g.user.uid).first()
        if goto_bucket:
            if user.video_name_temp:
                bucket.delete_object(user.video_name_temp)
            if user.cover_name_temp:
                bucket.delete_object(user.cover_name_temp)
        user.video_name_temp = ""
        user.cover_name_temp = ""
        db.session.commit()
    return success(message="取消成功")


@video_bp.route('/pv<int:id_>/like', methods=ALL_METHODS)
@auth.login_required
def like(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        if video.likes_user:
            likes = list(map(int, video.likes_user.split(',')))
            if user_id in likes:
                return params_error(message="已点赞")
            likes.append(user_id)
            video.likes_user = ','.join(str(i) for i in likes)
        else:
            likes = [user_id]
            video.likes_user = likes
        db.session.commit()
        data = {
            'likes': len(list(map(int, video.likes_user.split(',')))) if video.likes_user else 0
        }
        return success(message="点赞成功", data=data)
    else:
        return params_error(message="未查到视频信息")


@video_bp.route('/pv<int:id_>/unlike', methods=ALL_METHODS)
@auth.login_required
def unlike(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        if video.likes_user:
            likes = list(map(int, video.likes_user.split(',')))
            if user_id not in likes:
                return params_error(message="未点赞")
            likes.remove(user_id)
            if likes:
                video.likes_user = ','.join(str(i) for i in likes)
            else:
                video.likes_user = None
        else:
            return params_error(message="点赞数为0")
        data = {
            'likes': len(list(map(int, video.likes_user.split(',')))) if video.likes_user else 0
        }
        return success(message="取消点赞成功", data=data)
    else:
        return params_error(message="未查到视频信息")


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
            user.coins = coins_target + count / 2
            db.session.commit()
        data = {
            'coins': coins,
        }
        return success(message="投币成功", data=data)
    else:
        return params_error(message="未查到视频信息")


@video_bp.route('/pv<int:id_>/collect', methods=ALL_METHODS)
@auth.login_required
def collect(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user.collections:
            collections = list(map(int, user.collections.split(',')))
            if video.id in collections:
                return params_error(message="已收藏")
        video_collections = video.collections
        video_collections = video_collections + 1
        video.collections = video_collections
        pv = video.id
        db.session.commit()
        user = db.session.query(User).filter_by(id=user_id).first()
        if user.collections:
            collections = list(map(int, user.collections.split(',')))
            collections.append(pv)
            user.collections = ','.join(str(i) for i in collections)
        else:
            collections = [pv]
            user.collections = collections
        db.session.commit()
        data = {
            'video_collections': video_collections,
            'pv': pv
        }
        return success(message="收藏成功", data=data)
    else:
        return params_error(message="未查到视频信息")


@video_bp.route('/pv<int:id_>/un-collect', methods=ALL_METHODS)
@auth.login_required
def un_collect(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user.collections:
            collections = list(map(int, user.collections.split(',')))
            if video.id not in collections:
                return params_error(message="未收藏")
        video_collections = video.collections
        video_collections = video_collections - 1
        video.collections = video_collections
        pv = video.id
        db.session.commit()
        user = db.session.query(User).filter_by(id=user_id).first()
        if user.collections:
            collections = list(map(int, user.collections.split(',')))
            collections.remove(pv)
            if collections:
                user.collections = ','.join(str(i) for i in collections)
            else:
                user.collections = None
            db.session.commit()
        else:
            return params_error(message="收藏数为0")
        data = {
            'video_collections': video_collections,
            'collections': len(list(map(int, user.collections.split(',')))) if user.collections else 0,
            'pv': pv
        }
        return success(message="取消收藏成功", data=data)
    else:
        return params_error(message="未查到视频信息")


@video_bp.route("/pv<int:id_>/delete", methods=ALL_METHODS)
@auth.login_required
def delete(id_):
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if not user_id == video.uid:
        return unauthorized_error(message="没有权限")
    bucket.delete_object(video.video)
    bucket.delete_object(video.cover)
    db.session.delete(video)
    db.session.commit()
    return success(message="删除视频成功")


@video_bp.route('/pv<int:id_>/details', methods=ALL_METHODS)
@auth.login_required
def get_details(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        title = video.title
        collections = video.collections
        coins = video.coins
        uid = video.uid
        author = db.session.query(User).filter_by(id=uid).first()
        if not author:
            return params_error(message="未查到作者信息")
        is_liked = False
        if video.likes_user:
            likes_user = list(map(int, video.likes_user.split(',')))
            if g.user.uid in likes_user:
                is_liked = True
        else:
            is_liked = False
        is_collected = False
        user = db.session.query(User).filter_by(id=uid).first()
        if user.collections:
            collections = list(map(int, user.collections.split(',')))
            if video.id in collections:
                is_collected = True
        else:
            is_collected = False
        data = {
            'pv': video.id,
            'title': title,
            'type': video.type,
            'sign': video.sign,
            'duration': video.duration,
            'likes': len(list(map(int, video.likes_user.split(',')))) if video.likes_user else 0,
            'collections': collections,
            'coins': coins,
            'views': len(list(map(int, video.views.split(',')))) if video.views else 0,
            'comments': video.comments,
            'time': video.upload_time.strftime('%Y-%m-%d-%H-%M-%S'),
            'author': author.id,
            'bucket_cover': get_bucket_token(video.cover),
            'is_liked': is_liked,
            'is_collected': is_collected
        }
        return success(message="详情", data=data)
    else:
        return params_error(message="未查到视频信息")


@video_bp.route('/pv<int:id_>/video', methods=ALL_METHODS)
@auth.login_required
def get_video(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        if video.views:
            views = list(map(int, video.views.split(',')))
            if user_id not in views:
                views.append(user_id)
                video.views = ','.join(str(i) for i in views)
        else:
            video.views = [user_id]
        video_path = video.video
        db.session.commit()
        return success(message="视频", data=get_bucket_token(video_path))
    else:
        return params_error(message="未查到视频")


@video_bp.route('/pv<int:id_>/cover', methods=ALL_METHODS)
def get_cover(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    if video:
        cover_path = video.cover
        return success(message="视频封面", data=get_bucket_token(cover_path))
    else:
        return params_error(message="未查到视频封面")


@video_bp.route('/pv<int:id_>/comment', methods=ALL_METHODS)
@auth.login_required
def comment(id_):
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        form = VideoPutCommentForm()
        if form.validate_for_api() and form.validate():
            video.comments = video.comments + 1
            db.session.commit()
            comment_content = form.comment.data
            comment_new = Comment(content=comment_content, uid=user_id, target=id_)
            db.session.add(comment_new)
            db.session.commit()
            data = {
                'id': comment_new.id
            }
            return success(message="评论成功", data=data)
        else:
            return params_error(message=form.get_error())
    else:
        return params_error(message="未查到视频")


@video_bp.route("/pv<int:id_>/get-comment/type<int:type_>", methods=ALL_METHODS)
def get_comment(id_, type_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    if type_ == 0 or type_ == 1:
        video = db.session.query(Video).filter_by(id=id_).first()
        comment_id = []
        if video:
            if type_ == 1:
                all_comment = db.session.query(Comment).filter_by(target=id_, replay_id=None) \
                    .order_by(db.desc(Comment.likes_user)).all()
            else:
                all_comment = db.session.query(Comment).filter_by(target=id_, replay_id=None) \
                    .order_by(db.desc(Comment.upload_time)).all()
        else:
            return params_error(message="未找到视频")
        if all_comment:
            for comment_item in all_comment:
                comment_id.append(comment_item.id)
        data = {
            'all_comments': comment_id
        }
        return success(data=data, message="获取评论成功")
    else:
        return params_error("类型错误")


@video_bp.route('/pv<int:id_>/danmuku', methods=ALL_METHODS)
@auth.login_required
def danmuku(id_):
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    user_id = g.user.uid
    if video:
        form = VideoPutDanmukuForm()
        if form.validate_for_api() and form.validate():
            video.danmuku = video.danmuku + 1
            db.session.commit()
            danmuku_content = form.content.data
            danmuku_time = form.time.data
            danmuku_type = form.type.data
            danmuku_color = form.color.data
            danmuku_size = form.size.data
            danmuku_background = form.background.data
            danmuku_new = Danmuku(content=danmuku_content, time=danmuku_time, type=danmuku_type, color=danmuku_color
                                  , size=danmuku_size, background=danmuku_background, uid=user_id, target=id_)
            db.session.add(danmuku_new)
            db.session.commit()
            data = {
                'danmuku': video.danmuku
            }
            return success(message="发布弹幕成功", data=data)
        else:
            return params_error(message=form.get_error())
    else:
        return params_error(message="未查到视频")


@video_bp.route("/pv<int:id_>/get-danmuku", methods=ALL_METHODS)
def get_danmuku(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = db.session.query(Video).filter_by(id=id_).first()
    list_danmuku = []
    if video:
        all_danmuku = db.session.query(Danmuku).filter_by(target=id_)
    else:
        return params_error(message="未找到视频")
    if all_danmuku:
        for danmuku_item in all_danmuku:
            danmuku = {
                'id': danmuku_item.id,
                'content': danmuku_item.content,
                'time': danmuku_item.time,
                'type': danmuku_item.type,
                'color': danmuku_item.color,
                'size': danmuku_item.size,
                'background': danmuku_item.background,
                'author': danmuku_item.uid
            }
            list_danmuku.append(danmuku)
    data = {
        'all_danmuku': list_danmuku
    }
    return success(data=data, message="获取弹幕成功")


@video_bp.route("/list-video", methods=ALL_METHODS)
def list_video():
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    video = []
    all_video = db.session.query(Video).filter(Video.id).order_by(db.desc(Video.upload_time)).all()
    length = len(all_video)
    if length > 50:
        candidate_video = all_video[0:50]
    else:
        candidate_video = all_video[0:length]
    i = 1
    length = len(candidate_video)
    candidate_video.sort(key=lambda Video: (len(list(map(int, Video.views.split(',')))) if Video.views else 0)
                                           * 4 + Video.coins * 2 + Video.comments * 2 + Video.collections * 2,
                         reverse=True)
    if length < 8:
        for video_item in candidate_video:
            video.append(video_item.id)
    while i < 9 and length > 8:
        video_id = random.randint(1, length)
        if video_id in video:
            continue
        else:
            video.append(video_id)
            i += 1
    data = {
        'video_list': video
    }
    return success(data=data, message="获取视频成功")
