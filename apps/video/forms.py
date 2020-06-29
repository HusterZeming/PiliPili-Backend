from base_form import BaseForm, UploadBaseForm
from wtforms.validators import InputRequired, Length
from wtforms import StringField, IntegerField, FloatField, BooleanField
from flask_wtf.file import FileField, FileAllowed


class VideoUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('mp4')])


class VideoNewUploadForm(BaseForm):
    filename = StringField(validators=[Length(1, 80, message="文件名最多80字"), InputRequired(message="请输入文件名")])


class VideoNewCancelForm(BaseForm):
    goto_bucket = BooleanField(InputRequired(message="请输入取消类型"))


class ImageUploadForm(UploadBaseForm):
    content = FileField(validators=[FileAllowed('jpg', 'png')])


class VideoSaveForm(BaseForm):
    title = StringField(validators=[Length(1, 80, message="标题最多80字"), InputRequired(message="请输入视频标题")])
    sign = StringField(validators=[Length(0, 233, message="简介最多233字")])
    type = IntegerField(validators=[InputRequired(message="请输入视频类分类")])
    duration = StringField(validators=[Length(1, 80, message="时长最多80位"), InputRequired(message="请输入视频时长")])


class VideoPutCoinForm(BaseForm):
    coins = IntegerField(validators=[InputRequired(message="请输入投币个数")])


class VideoPutCommentForm(BaseForm):
    comment = StringField(validators=[Length(1, 500, message="评论最多500字"), InputRequired(message="请输入评论")])


class VideoPutDanmukuForm(BaseForm):
    content = StringField(validators=[Length(1, 500, message="弹幕最多50字"), InputRequired(message="请输入弹幕")])
    time = FloatField(validators=[InputRequired(message="请输入时间")])
    type = IntegerField(validators=[InputRequired(message="请输入类型")])
    color = StringField(validators=[Length(1, 500, message="颜色最多20字"), InputRequired(message="请输入颜色")])
    size = IntegerField()
    background = IntegerField()

