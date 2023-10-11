from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    code = 403
    message = '403 Forbidden'


class InputError(HTTPException):
    code = 400
    message = '400 Bad Request'
