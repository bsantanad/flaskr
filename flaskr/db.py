import sqlite3

import click
import flask

def get_db():
    '''
    check if db already in flask.g, if not create new
    connection
    '''
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES,
        )
        # return rows that behave like dicts
        # FIXME check why is this not working, it is returning tuple not dict
        flask.g.row_factory = sqlite3.Row
    return flask.g.db

def close_db(e = None):
    db = flask.g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with flask.current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click defines a command line command
@click.command('init-db')
def init_db_command():
    '''
    clear the exsisting data and create new tables
    '''
    init_db()
    click.echo('init the db')

def init_app(app):
    # teardown tells flask to call this when cleaning up after returning a
    # response
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
