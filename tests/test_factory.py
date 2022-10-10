import flaskr

def test_config():
    assert not flaskr.create_app().testing
    assert flaskr.create_app({'TESTING': True}).testing

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'hello world'
