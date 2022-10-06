import os

import flask

def create_app(test_config = None):
    # create and config the app
    app = flask.Flask(
        __name__, # flaskr
        instance_relative_config = True, # path relative to instance folder
    )
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        # load the test config if padded in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # from db.py
    from . import db
    db.init_app(app)

    # from auth.py blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/hello')
    def hello():
        return 'hello world'

    return app
