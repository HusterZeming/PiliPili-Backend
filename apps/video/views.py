from flask import request

from flask import Blueprint, g

from apps.user.verify_token import auth
from config import ALL_METHODS

from ..libs.error_code import NotFound, RequestMethodNotAllowed
from ..libs.restful import params_error, success
from models import Video

bp = Blueprint('note', __name__, url_prefix='/note')


@bp.route('/publish/', methods=ALL_METHODS)
@auth.login_required
def publish():
    """
    1.验证POST方法，验证token信息
    2.进行JSON数据格式和表单验证，验证成功后通过g.user获取用户uid,然后像数据库插入数据，
    返回success,否则返回参数错误
    :return: success or params_error
    """
    if request.method != 'POST':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)

    form = NotePublishForm()
    if form.validate_for_api() and form.validate():
        title = form.title.data
        content = form.content.data
        uid = g.user.uid
        article = Note(title=title, content=content, uid=uid)
        dbsession.add(article)
        dbsession.commit()
        return success(message="发布文章成功")
    else:
        return params_error(message=form.get_error())


# 修改指定为put方法
@bp.route('/modify/', methods=ALL_METHODS)
@auth.login_required
def modify():

    if request.method != 'PUT':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    dbsession = DBSession.make_session()
    form = NoteModifyForm()
    if form.validate_for_api() and form.validate():
        article_id = form.id.data
        title = form.title.data
        content = form.content.data
        article = dbsession.query(Note).filter_by(id=article_id).first()
        if article:
            article.title = title
            article.content = content
            dbsession.commit()
            return success(message="修改文章成功")
    else:
        return params_error(message=form.get_error())


@bp.route("/delete/", methods=ALL_METHODS)
@auth.login_required
def delete():

    if request.method != 'DELETE':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    dbsession = DBSession.make_session()
    form = ArticleDeleteForm()
    if form.validate_for_api and form.validate():
        article_id = form.id.data
        article = dbsession.query(Note).filter_by(id=article_id).first()
        dbsession.delete(article)
        dbsession.commit()
        return success(message="删除文章成功")
    else:
        return params_error(message=form.get_error())


@bp.route('/list_all/', methods=ALL_METHODS)
def list_all():

    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    dbsession = DBSession.make_session()
    article_titles = []
    articles = dbsession.query(Note).filter(Note.id).all()
    if articles:
        for article in articles:
            article_titles.append(article.title)
    return success(data={"all_articles": article_titles}, message="获取文章列表成功")


@bp.route('/details/<int:id_>',methods=ALL_METHODS)
def details(id_):

    if request.method != 'GET':
        raise RequestMethodNotAllowed(msg="The method %s is not allowed for the requested URL" % request.method)
    dbsession = DBSession.make_session()
    article = dbsession.query(Note).filter_by(id=id_).first()
    if article:
        title = article.title
        content = article.content
        return success(message="这是文章详情页", data={'文章标题': title, '文章内容': content})
    else:
        raise NotFound(msg='没有找到您要查看的文章')
