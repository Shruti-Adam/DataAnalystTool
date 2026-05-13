from django.apps import AppConfig
import os


class DashboardConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'

    name = 'dashboard'

    def ready(self):

        if os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from .scheduler import start_scheduler
            start_scheduler()

        except Exception as e:
            print("Scheduler startup error:", e)