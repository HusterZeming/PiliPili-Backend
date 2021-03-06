from flask import request
from flask import Blueprint, g
from apps.user.verify_token import auth
from config import ALL_METHODS
from ..libs.bucket_get_token import get_bucket_token
from ..libs.error_code import RequestMethodNotAllowed
from ..libs.restful import params_error, success, unauthorized_error
from .forms import CommentReplyForm
from exts import db
from models import Video, Comment, User

comment_bp = Blueprint('comment', __name__, url_prefix='/comment')


@comment_bp.route('/comment<int:id_>/like', methods=ALL_METHODS)
@auth.login_required
def like(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    user_id = g.user.uid
    if comment:
        if comment.likes_user:
            likes = list(map(int, comment.likes_user.split(',')))
            if user_id in likes:
                return params_error(message="已点赞")
            likes.append(user_id)
            comment.likes_user = ','.join(str(i) for i in likes)
        else:
            likes = [user_id]
            comment.likes_user = likes
        db.session.commit()
        data = {
            'likes': len(list(map(int, comment.likes_user.split(',')))) if comment.likes_user else 0
        }
        return success(message="点赞成功", data=data)
    else:
        return params_error(message="未查到评论信息")


@comment_bp.route('/comment<int:id_>/unlike', methods=ALL_METHODS)
@auth.login_required
def unlike(id_):
    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    user_id = g.user.uid
    if comment:
        if comment.likes_user:
            likes = list(map(int, comment.likes_user.split(',')))
            if user_id not in likes:
                return params_error(message="未点赞")
            likes.remove(user_id)
            if likes:
                comment.likes_user = ','.join(str(i) for i in likes)
            else:
                comment.likes_user = None
            db.session.commit()
        else:
            return params_error(message="点赞数为0")
        data = {
            'likes': len(list(map(int, comment.likes_user.split(',')))) if comment.likes_user else 0
        }
        return success(message="取消点赞成功", data=data)
    else:
        return params_error(message="未查到评论信息")


@comment_bp.route("/comment<int:id_>/delete", methods=ALL_METHODS)
@auth.login_required
def delete(id_):
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    if not comment.target:
        return params_error(message="未查到评论的所属视频信息")
    video = db.session.query(Video).filter_by(id=comment.target).first()
    user_id = g.user.uid
    if not user_id == comment.uid and not user_id == video.uid:
        return unauthorized_error(message="没有权限")
    db.session.delete(comment)
    db.session.commit()
    if video:
        all_comments = db.session.query(Comment).filter_by(target=video.id).all()
        video.comments = len(all_comments) if all_comments else 0
        db.session.commit()
    return success(message="删除评论成功")


@comment_bp.route("/comment<int:id_>/replay", methods=ALL_METHODS)
@auth.login_required
def replay(id_):
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    form = CommentReplyForm()
    if form.validate_for_api() and form.validate():
        comment_content = form.comment.data
        comment_replay = Comment(content=comment_content, uid=g.user.uid, target=comment.target, replay_id=comment.id)
        db.session.add(comment_replay)
        db.session.commit()
        video = db.session.query(Video).filter_by(id=comment.target).first()
        if video:
            all_comments = db.session.query(Comment).filter_by(target=video.id).all()
            video.comments = len(all_comments) if all_comments else 0
            db.session.commit()
        data = {
            'id': comment_replay.id
        }
    else:
        return params_error(message=form.get_error())
    return success(message="回复成功", data=data)


@comment_bp.route("/comment<int:id_>/get-replay", methods=ALL_METHODS)
@auth.login_required
def get_replay(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    replay_list = []
    replay_all = []
    if comment:
        dfs(replay_list, id_)
    else:
        return params_error(message="未找到评论")
    if replay_list:
        count = 0
        for comment_item in replay_list:
            replay_to = db.session.query(Comment).filter_by(id=comment_item.replay_id).first()
            if replay_to:
                user = db.session.query(User).filter_by(id=replay_to.uid).first()
            is_liked = False
            if comment_item.likes_user:
                likes = list(map(int, comment_item.likes_user.split(',')))
                if g.user.uid in likes:
                    is_liked = True
            author = db.session.query(User).filter_by(id=comment_item.uid).first()
            comment = {
                'id': comment_item.id,
                'content': comment_item.content,
                'likes': len(list(map(int, comment_item.likes_user.split(',')))) if comment_item.likes_user else 0,
                'time': comment_item.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'replay_id': comment_item.replay_id,
                'author': comment_item.uid,
                'author_name': author.username,
                'replay_to_author': user.id if replay_to else None,
                'replay_to_author_name': user.username if replay_to else None,
                'is_liked': is_liked
            }
            replay_all.append(comment)
            count += 1
            if count > 3:
                break
    data = {
        'all_comments': replay_all
    }
    return success(data=data, message="获取回复成功")


@comment_bp.route("/comment<int:id_>/get-replay-dfs", methods=ALL_METHODS)
@auth.login_required
def get_replay_dfs(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    replay_list = []
    replay_all = []
    if comment:
        dfs(replay_list, id_)
    else:
        return params_error(message="未找到评论")
    if replay_list:
        for comment_item in replay_list:
            replay_to = db.session.query(Comment).filter_by(id=comment_item.replay_id).first()
            if replay_to:
                user = db.session.query(User).filter_by(id=replay_to.uid).first()
            is_liked = False
            if comment_item.likes_user:
                likes = list(map(int, comment_item.likes_user.split(',')))
                if g.user.uid in likes:
                    is_liked = True
            author = db.session.query(User).filter_by(id=comment_item.uid).first()
            comment = {
                'id': comment_item.id,
                'content': comment_item.content,
                'likes': len(list(map(int, comment_item.likes_user.split(',')))) if comment_item.likes_user else 0,
                'time': comment_item.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'replay_id': comment_item.replay_id,
                'author': comment_item.uid,
                'author_name': author.username,
                'replay_to_author': user.id if replay_to else None,
                'replay_to_author_name': user.username if replay_to else None,
                'is_liked': is_liked
            }
            replay_all.append(comment)
    data = {
        'all_comments': replay_all
    }
    return success(data=data, message="获取回复成功")


def dfs(replay_list, id):
    all_replay = db.session.query(Comment).filter_by(replay_id=id).all()
    if all_replay:
        for replay_item in all_replay:
            replay_list.append(replay_item)
            dfs(replay_list, replay_item.id)


@comment_bp.route("/comment<int:id_>/details", methods=ALL_METHODS)
@auth.login_required
def details(id_):
    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    if comment:
        replay_to = db.session.query(Comment).filter_by(id=comment.replay_id).first()
        if replay_to:
            user = db.session.query(User).filter_by(id=replay_to.uid).first()
        is_liked = False
        if comment.likes_user:
            likes = list(map(int, comment.likes_user.split(',')))
            if g.user.uid in likes:
                is_liked = True
        author = db.session.query(User).filter_by(id=comment.uid).first()
        data = {
                'id': comment.id,
                'content': comment.content,
                'likes': len(list(map(int, comment.likes_user.split(',')))) if comment.likes_user else 0,
                'time': comment.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'replay_id': comment.replay_id,
                'author': comment.uid,
                'author_name': author.username,
                'replay_to_author': user.id if replay_to else None,
                'replay_to_author_name': user.username if replay_to else None,
        }
        return success(data=data, message="获取评论成功")
    else:
        return params_error(message="未查到评论")
