from base_form import BaseForm, UploadBaseForm
from wtforms.validators import InputRequired
from wtforms import StringField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask import g
from models import Video, User
from exts import db
from apps.libs.error_code import NotFound, AuthFailed


class VideoUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('mp4')])


class ImageUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('jpg', 'png')])


class VideoSaveForm(BaseForm):
    title = StringField(validators=[InputRequired(message="请输入文章标题")])
    video = StringField(validators=[InputRequired(message="请输入目标视频")])
    cover = StringField(validators=[InputRequired(message="请输入目标封面")])


class VideoPutCoinForm(BaseForm):
    coins = IntegerField(validators=[InputRequired(message="请输入投币个数")])


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
