from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        from .scheduler import start_scheduler

        try:
            start_scheduler()
        except Exception as e:
            print("Scheduler startup error:", e)