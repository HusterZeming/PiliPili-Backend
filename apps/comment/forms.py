from base_form import BaseForm
from wtforms.validators import InputRequired, Length
from wtforms import StringField


class CommentReplyForm(BaseForm):
    comment = StringField(validators=[Length(1, 500, message="评论最多500字"), InputRequired(message="请输入评论")])


