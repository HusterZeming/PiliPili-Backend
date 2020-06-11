# encoding: utf-8
# 定义几个简单的restful-api
from flask import jsonify


class HttpCode(object):
    ok = 200
    unauthorized_error = 401
    params_error = 400
    server_error = 500


def restful_result(code, message, data):
    return jsonify({"code": code, "message": message, "data": data or {}})


def success(message="", data=None):
    return restful_result(code=HttpCode.ok, message=message, data=data)


def unauthorized_error(message=""):
    return jsonify({"code": HttpCode.unauthorized_error, "message": message})


def params_error(message=""):
    return jsonify({"code": HttpCode.params_error, "message": message})


def server_error(message=""):
    return jsonify({"code": HttpCode.unauthorized_error, "message": message or "服务器内部错误"})
