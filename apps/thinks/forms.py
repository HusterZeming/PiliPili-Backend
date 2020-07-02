from base_form import BaseForm
from wtforms.validators import InputRequired, Length
from wtforms import StringField, IntegerField


class ThinkUploadForm(BaseForm):
    content = StringField(validators=[Length(1, 200, message="动态最多200字"), InputRequired(message="请输入动态")])
    video = IntegerField()


class ThinkUploadPhotoForm(BaseForm):
    photo = StringField(validators=[Length(1, 80, message="图片文件名最多80字"), InputRequired(message="请输入图片名")])
