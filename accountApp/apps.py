from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accountApp'

    def ready(self):
        import accountApp.signals  # noqa
