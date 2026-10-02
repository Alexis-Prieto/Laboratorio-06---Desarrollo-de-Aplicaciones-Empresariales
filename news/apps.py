"""Application configuration for the news app."""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration class for the news application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
