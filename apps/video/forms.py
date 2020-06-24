from base_form import BaseForm, UploadBaseForm
from wtforms.validators import InputRequired, Length
from wtforms import StringField, IntegerField, FloatField
from flask_wtf.file import FileField, FileAllowed
from flask import g
from models import Video, User
from exts import db
from apps.libs.error_code import NotFound, AuthFailed


class VideoUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('mp4')])


class ImageUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('jpg', 'png')])


class VideoSaveForm(BaseForm):
    title = StringField(validators=[InputRequired(message="请输入视频标题")])
    sign = StringField(validators=[InputRequired(message="请输入视频简介")])
    type = IntegerField(validators=[InputRequired(message="请输入视频类分类")])


class VideoPutCoinForm(BaseForm):
    coins = IntegerField(validators=[InputRequired(message="请输入投币个数")])


class VideoPutCommentForm(BaseForm):
    comment = StringField(validators=[Length(1, 500, message="评论最多500字"), InputRequired(message="请输入评论")])


class VideoGetCommentForm(BaseForm):
    type = IntegerField(validators=[InputRequired(message="请输入排序类型")])


class VideoPutDanmukuForm(BaseForm):
    content = StringField(validators=[Length(1, 500, message="弹幕最多50字"), InputRequired(message="请输入弹幕")])
    time = FloatField(validators=[InputRequired(message="请输入时间")])
    type = IntegerField(validators=[InputRequired(message="请输入类型")])
    color = StringField(validators=[Length(1, 500, message="颜色最多20字"), InputRequired(message="请输入颜色")])
    size = IntegerField()
    background = IntegerField()


class VideoDeleteForm(BaseForm):
    pv = IntegerField(validators=[InputRequired(message="请输入pv号")])

    # 验证id是否合法
    def validate_id(self, id_):

        user = db.dbsesson.query(User).filter_by(id=g.user.uid).first()
        id_s1 = []
        id_s2 = []
        for video in user.videos:
            id_s1.append(video.id)
        videos = db.dbsesson.query(Video).filter(Video.id).all()
        for video in videos:
            id_s2.append(video.id)
        if id_.data not in id_s2:
            raise NotFound(msg="找不到删除的视频")
        if id_.data not in id_s1:
            raise AuthFailed(msg="没有删除该视频的权限")
