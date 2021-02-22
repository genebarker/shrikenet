from flask import Blueprint, g

from shrikenet.api.token_authority import token_required


bp = Blueprint('hello_json', __name__, url_prefix='/api')


@bp.route('/hello')
def hello_json():
    return {
        'error_code': 0,
        'message': 'Hello, World!',
    }


@bp.route('/hello-get')
@token_required
def hello_get():
    return {
        'error_code': 0,
        'message': 'Hello, GET!',
        'username': g.user.username,
        'user_oid': g.user.oid,
        'http_method': 'GET',
    }
