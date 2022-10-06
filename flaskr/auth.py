import functools

import flask
import werkzeug.security
import flask.db

# creates blueprint
# (
#  named auth,
#  where it's defined,
#  will be prepended to all urls associated to this blueprint
# )
bp = flask.Blueprint('auth', __name__, url_prefix = '/auth')

# when user calls /auth/register
@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        db = flask.db.get_db()
        error = None

        if not username:
            error = 'username is required'
        if not password:
            error = 'password is required'

        if error is None:
            try:
                # takes care of sql injections
                db.execute(
                    'INSERT INTO user (username, password) values (?, ?)',
                    (
                        username,
                        werkzeug.security.generate_password_hash(password)
                    ),
                )
                db.commit()
            except db.IntegrityError:
                error = f'user {username} is already registered'
            else:
                return flask.redirect(flask.url_for('auth.login'))

        flask.flash(error)

    return flask.render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        passwd = flask.request.form['password']
        db = flask.db.get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,),
        ).fetchone()

        if user is None:
            error = 'incorrect username'
        if not werkzeug.security.check_password_hash(user['password'], passwd):
            error = 'incorrect password'

        if error is None:
            # session is a dict that stores data across requests. When
            # validation succeeds, the user’s id is stored in a new session.
            # The data is stored in a cookie that is sent to the browser, and
            # the browser then sends it back with subsequent requests. Flask
            # securely signs the data so that it can’t be tampered with.
            flask.session.clear()
            flask.session['user_id'] = user['id']
            return flask.redirect(flask.url_for('index'))

        flask.flash(error)

    return flask.render_template('auth/login.html')

# registers function that runs before the view function
@bp.before_app_request
def load_logged_in_user():
    user_id = flask.session.get('user_id')

    if user_id is None:
        flask.g.user = None
    else:
        flask.g.user = get_db().execute(
            'SELECT * FROM user WEHRE id = ?',
            (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return flask.redirect(flask.url_for('index'))

def login_required(view):
    '''
    this decorator checks if a user is logged in, if not it redirects them to
    the login page
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if flask.g.user in None:
            return flask.redirect(flask.url_for('auth.login'))
        return views(**kwargs)    

    return wrapped_view
