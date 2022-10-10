import os
import tempfile

import pytest
import flaskr
import flaskr.db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = flaskr.create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        flaskr.db.init_db()
        flaskr.db.get_db().executescript(_data_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_client()
