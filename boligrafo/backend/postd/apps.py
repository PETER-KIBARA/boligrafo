from django.apps import AppConfig


class PostdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "postd"

    def ready(self):
        import postd.signals  # your signal connections

        # Import and start scheduler *properly*
        try:
            from . import scheduler  # this actually defines it
            scheduler.start()
        except Exception as e:
            print(f"⚠️ Scheduler failed to start: {e}")
