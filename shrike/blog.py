from datetime import date, datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from shrike.auth import login_required
from shrike.db import get_services
from shrike.entities.post import Post

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    storage_provider = get_services().storage_provider
    posts = storage_provider.get_posts()
    today = date.today()
    return render_template('blog/index.html', posts=posts, today=today)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            storage_provider = get_services().storage_provider
            post = Post(
                oid=storage_provider.get_next_post_oid(),
                title=title,
                body=body,
                author_oid=g.user.oid,
                created_time=datetime.now().astimezone(),
            )
            storage_provider.add_post(post)
            storage_provider.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    storage_provider = get_services().storage_provider
    try:
        post = storage_provider.get_post_by_oid(id)
    except KeyError:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author_oid != g.user.oid:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            storage_provider = get_services().storage_provider
            post.title = title
            post.body = body
            storage_provider.update_post(post)
            storage_provider.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    storage_provider = get_services().storage_provider
    storage_provider.delete_post_by_oid(id)
    storage_provider.commit()
    return redirect(url_for('blog.index'))
