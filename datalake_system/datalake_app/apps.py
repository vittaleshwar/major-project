from django.apps import AppConfig

class DatalakeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datalake_app'
    
    def ready(self):
        import datalake_app.signals