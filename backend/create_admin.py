import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bloodpressure.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("✅ Superuser created")
else:
    print("ℹ️ Superuser already exists — skipping creation")
