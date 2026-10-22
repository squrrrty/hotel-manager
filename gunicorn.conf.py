"""Настройки HTTP-сервера для Linux-хостинга; Flask-приложение — run:app."""
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 2
accesslog = "-"
errorlog = "-"
timeout = 60
