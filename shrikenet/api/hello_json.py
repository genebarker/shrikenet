from flask import Blueprint, g, request

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
    return hello_data('GET')


def hello_data(http_method):
    return {
        'error_code': 0,
        'message': f'Hello, {g.user.name}!',
        'username': g.user.username,
        'user_oid': g.user.oid,
        'http_method': http_method,
        'http_payload': request.get_json(),
    }


@bp.route('/hello-post', methods=['POST'])
@token_required
def hello_post():
    return hello_data('POST')


@bp.route('/hello-put', methods=['PUT'])
@token_required
def hello_put():
    return hello_data('PUT')


@bp.route('/hello-delete', methods=['DELETE'])
@token_required
def hello_delete():
    return hello_data('DELETE')
