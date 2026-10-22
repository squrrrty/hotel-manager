import os
import subprocess
import sys

import pytest


def production_import(**overrides):
    env = dict(os.environ, APP_ENV='production',
               SECRET_KEY='s' * 40,
               DATABASE_URL='postgresql://test:unused@127.0.0.1:5433/not_connected')
    env.update(overrides)
    return subprocess.run([sys.executable, '-c',
        'from run import app; '
        'assert not app.debug; '
        'assert app.config["SESSION_COOKIE_SECURE"]; '
        'assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg2://"); '
        'assert "admin123" not in app.test_client().get("/login").text'],
        env=env, capture_output=True, text=True)


@pytest.mark.parametrize('prefix', ['postgres://', 'postgresql://', 'postgresql+psycopg2://'])
def test_hosting_database_url(prefix):
    result = production_import(DATABASE_URL=prefix + 'test:unused@127.0.0.1:5433/not_connected')
    assert result.returncode == 0, result.stderr


def test_production_requires_secret():
    result = production_import(SECRET_KEY='dev')
    assert result.returncode != 0
    assert 'SECRET_KEY' in result.stderr


def test_csrf_protects_post(app):
    app.config['CSRF_ENABLED'] = True
    client = app.test_client()
    assert client.post('/login', data={'username': 'admin', 'password': 'admin123'}).status_code == 400
    assert client.get('/login').status_code == 200
    with client.session_transaction() as session:
        token = session['_csrf_token']
    result = client.post('/login', data={
        'username': 'admin', 'password': 'admin123', '_csrf_token': token})
    assert result.status_code == 302
