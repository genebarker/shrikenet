from flask import Blueprint


bp = Blueprint('hello_json', __name__, url_prefix='/api')


@bp.route('/hello')
def hello_json():
    return {
        'error_code': 0,
        'message': 'Hello, World!',
    }
