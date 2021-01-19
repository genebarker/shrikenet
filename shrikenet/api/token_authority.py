from datetime import datetime, timedelta, timezone
import functools
import logging

from flask import Blueprint, current_app, g, request
import jwt

from shrikenet.db import get_services
from shrikenet.usecases.login_to_system import LoginToSystem

logger = logging.getLogger(__name__)
bp = Blueprint('token_authority', __name__, url_prefix='/api')


@bp.route('/get_token', methods=['POST'])
def get_token():
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    ip_address = request.remote_addr
    login_to_system = LoginToSystem(get_services())
    login_result = login_to_system.run(username, password, ip_address)
    if login_result.has_failed:
        return {
            'error_code': 2,
            'message': login_result.message,
        }
    expire_time = datetime.now(timezone.utc) + timedelta(days=30)
    secret_key = current_app.config['SECRET_KEY']
    token = create_token(login_result.user_oid, expire_time, secret_key)
    return {
        'error_code': 0,
        'message': login_result.message,
        'token': token,
        'expire_time': f'{expire_time}',
    }


def create_token(user_oid, expire_time, secret_key):
    payload = {'user_oid': user_oid, 'exp': expire_time}
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def token_required(api):
    @functools.wraps(api)
    def wrapped_api(**kwargs):
        try:
            token = request.headers.get('TOKEN')
            if token is None or token == '':
                error_code = 1
                message = 'An authorization token is required.'
                logger.info(
                    'Method access denied from %s since no token provided '
                    '(error_code=%d, method=%s).',
                    request.remote_addr,
                    error_code,
                    api.__name__,
                )
                return {
                    'error_code': error_code,
                    'message': message,
                }

            secret_key = current_app.config['SECRET_KEY']
            try:
                payload = jwt.decode(
                    token, secret_key, algorithms=['HS256', ]
                )
                user_oid = payload['user_oid']
                db = get_services().storage_provider
                g.user = db.get_app_user_by_oid(user_oid)
            except jwt.ExpiredSignatureError:
                error_code = 4
                message = 'The authorization token has expired.'
                expire_time = get_expire_time(token, secret_key)
                logger.info(
                    'Method access denied from %s since the token has '
                    'expired (error_code=%d, method=%s, '
                    'expire_time=\'%s\').',
                    request.remote_addr,
                    error_code,
                    api.__name__,
                    str(expire_time),
                )
                return {
                    'error_code': error_code,
                    'message': message,
                }
            except jwt.InvalidTokenError as error:
                error_code = 3
                message = 'The provided authorization token is invalid.'
                logger.info(
                    'Method access denied from %s due to an invalid token '
                    '(error_code=%d, method=%s). Reason: %s',
                    request.remote_addr,
                    error_code,
                    api.__name__,
                    str(error),
                )
                return {
                    'error_code': error_code,
                    'message': message,
                }

            return api(**kwargs)

        except Exception as error:
            error_code = 5
            message = (
                'An unexpected error occurred when processing the '
                'authorization token.'
            )
            logger.info(
                'Method access denied from %s since an unexpected error '
                'occurred while processing the token (error_code=%d, '
                'method=%s). Reason: %s',
                request.remote_addr,
                error_code,
                api.__name__,
                str(error),
            )
            return {
                'error_code': error_code,
                'message': message,
            }

    return wrapped_api


def get_expire_time(token, secret_key):
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=['HS256', ],
        options={'verify_signature': False},
    )
    return datetime.fromtimestamp(payload['exp'])


@bp.route('/verify_token', methods=['POST'])
@token_required
def verify_token():
    return {
        'error_code': 0,
        'message': (
            f'valid token provided (user_oid={g.user.oid}, '
            f'username={g.user.username})'
        )
    }
