from flask import json
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    """
    code:错误码
    msg:错误信息
    需要重写get_body方法以返回JSON数据，而不是表单数据。
    需要重写get_header方法设置头部ContentType为application/json
    """
    code = 500
    msg = "Sorry, Some mistakes occurred"

    def __init__(self, msg=None, code=None, data=None):
        if msg:
            self.msg = msg
        if code:
            self.code = code
        if data:
            self.data = data
        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            message=self.msg,
            code=self.code,
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]
