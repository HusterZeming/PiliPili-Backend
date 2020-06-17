from exts import db
from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

bind_key = None


class User(db.Model):
    """
    表名user
    id:主键
    username:用户名
    _password:password 密码 sha256加密
    email:邮箱
    join_time:用户注册时间
    """
    __bind_key__ = bind_key
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    coins = db.Column(db.Integer, default=0)
    join_time = db.Column(db.DateTime, default=datetime.now)
    collections = db.Column(db.Text(5000))
    fans = db.Column(db.Text(10000))
    followings = db.Column(db.Text(10000))
    avatar = db.Column(db.String(100))
    background = db.Column(db.String(100))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        return self._password

    # hash加密
    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    # 验证密码
    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result


class Video(db.Model):
    __bind_key__ = bind_key
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    collections = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)
    views = db.Column(db.Text(10000))
    comments = db.Column(db.Integer, default=0)
    likes_user = db.Column(db.Text(10000))
    upload_time = db.Column(db.DateTime, default=datetime.now)
    # 建立外键关联
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = relationship("User", backref="videos")


class Comment(db.Model):
    __bind_key__ = bind_key
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500), nullable=False)
    likes_user = db.Column(db.Text(10000))
    upload_time = db.Column(db.DateTime, default=datetime.now)
    # 建立外键关联
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = relationship("User", backref="comments_user")
    target = db.Column(db.Integer, db.ForeignKey("video.id", ondelete='CASCADE', onupdate='CASCADE'))
    replay_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete='CASCADE', onupdate='CASCADE'))

