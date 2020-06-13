from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder
from datetime import date
import config
from exts import db
from apps.libs.error_code import ServerError
from apps.user.views import user_bp
from apps.video.views import video_bp


class JSONEncoder(_JSONEncoder):

    def default(self, o):
        if hasattr(0, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        # 时间类型是不能被序列化的
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        raise ServerError()


# 更改json_encoder
class Flask(_Flask):
    json_encoder = JSONEncoder


def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    app.register_blueprint(video_bp)
    app.config.from_object(config)
    db.init_app(app)
    return app


if __name__ == '__main__':
    app_ = create_app()
    # 运行在8080端口
    app_.run(port=5000)
