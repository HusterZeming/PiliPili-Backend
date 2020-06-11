from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def generate_token(uid, expiration=259200):

    # 加密id来生成token 有效期3天
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'uid': uid})
