import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from shrike.db import get_services
from shrike.entities.app_user import AppUser
from shrike.usecases.login_to_system import LoginToSystem

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        storage_provider = get_services().storage_provider
        crypto_provider = get_services().crypto_provider
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif storage_provider.exists_app_username(username):
            error = 'User {} is already registered.'.format(username)

        if error is None:
            new_user = AppUser(
                oid=storage_provider.get_next_app_user_oid(),
                username=username,
                name=None,
                password_hash=crypto_provider.generate_hash_from_string(
                    password),
            )
            storage_provider.add_app_user(new_user)
            storage_provider.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_to_system = LoginToSystem(get_services())
        login_result = login_to_system.run(username, password)

        if login_result.has_failed:
            flash(login_result.message)
            return render_template('auth/login.html')

        session.clear()
        session['user_id'] = login_result.user_oid
        return redirect(url_for('index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_services().storage_provider.get_app_user_by_oid(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
