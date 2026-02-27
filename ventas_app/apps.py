from django.apps import AppConfig


class VentasAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas_app'

    def ready(self):
        import ventas_app.signals
