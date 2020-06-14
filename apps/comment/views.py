from flask import request
from flask import Blueprint, g
from apps.user.verify_token import auth
from config import ALL_METHODS
from ..libs.error_code import NotFound, RequestMethodNotAllowed
from ..libs.restful import params_error, success, unauthorized_error
from .forms import CommentReplyForm
from exts import db
from models import Video, Comment

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
        raise NotFound(msg='未查到评论信息')


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
        raise NotFound(msg='未查到评论信息')


@comment_bp.route("/comment<int:id_>/delete", methods=ALL_METHODS)
@auth.login_required
def delete(id_):
    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    comment = db.session.query(Comment).filter_by(id=id_).first()
    user_id = g.user.uid
    if not user_id == comment.uid:
        return unauthorized_error(message="没有权限")
    video = db.session.query(Video).filter_by(id=comment.target).first()
    if video:
        video.comments = video.comments - 1 if video.comments else 0
    db.session.delete(comment)
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
    else:
        return params_error(message=form.get_error())
    return success(message="回复成功")
