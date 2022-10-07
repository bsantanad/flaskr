import flask
import werkzeug.exceptions

import flaskr.auth
import flaskr.db

bp = flask.Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = flaskr.db.get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return flask.render_template('blog/index.html', posts = posts)

@bp.route('/create', methods = ('GET', 'POST'))
@flaskr.auth.login_required
def create():
    if flask.request.method == 'POST':
        title = flask.request.form['title']
        body = flask.request.form['body']
        error = None

        if not title:
            error = 'title is required'

        if error is not None:
            flask.flash(error)
        else:
            db = flaskr.db.get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, flask.g.user['id'])
            )
            db.commit()
            return flask.redirect(flask.url_for('blog.index'))

    return flask.render_template('blog/create.html')

def get_post(id, check_author = True):
    post = flaskr.db.get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        werkzeug.exceptions.abort(404, f'post id {id} does not exists')

    if check_author and post['author_id'] != flask.g.user['id']:
        werkzeug.exceptions.abort(403)

    return post

@bp.route('/<int:id>/update', methods = ('GET', 'POST'))
@flaskr.auth.login_required
def update(id):
    post = get_post(id)

    if flask.request.method == 'POST':
        title = flask.request.form['title']
        body = flask.request.form['body']
        error = None

        if not title:
            error = 'title is required'

        if error is not None:
            flask.flash(error)
        else:
            db = flaskr.db.get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return flask.redirect(flask.url_for('blog.index'))

    return flask.render_template('blog/update.html', post = post)

@bp.route('/<int:id>/delete', methods = ('POST',))
@flaskr.auth.login_required
def delete(id):
    get_post(id)
    db = flaskr.db.get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return flask.redirect(flask.url_for('blog.index'))
