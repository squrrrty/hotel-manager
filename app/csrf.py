"""Токен формы защищает POST-запросы от отправки с постороннего сайта."""
import secrets
from flask import abort, request, session


def init_csrf(app):
    def csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_urlsafe(32)
        return session['_csrf_token']

    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def check_csrf():
        if request.method == 'POST' and app.config.get('CSRF_ENABLED', True):
            expected = session.get('_csrf_token', '')
            supplied = request.form.get('_csrf_token', '')
            if not expected or not secrets.compare_digest(expected.encode(), supplied.encode()):
                abort(400, description='Обновите страницу и повторите отправку формы.')
