from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from postd.models import VitalReading, Notification, UserProfile
from django.conf import settings

scheduler = BackgroundScheduler()

def check_daily_bp():
    """Check if patients have logged at least 2 BP readings today."""
    print("🩺 Checking daily BP logs...")
    today = timezone.now().date()

    for profile in UserProfile.objects.select_related("user", "doctor"):
        # 🛑 Skip profiles without an assigned doctor
        if not profile.doctor:
            print(f"⚠️ Skipping {profile.user.username} — no assigned doctor.")
            continue

        count = VitalReading.objects.filter(
            patient=profile.user,
            created_at__date=today
        ).count()

        if count < 2:
            Notification.objects.create(
                doctor=profile.doctor.user,  # guaranteed non-null now
                patient=profile,
                title="Missed BP Reading",
                message=f"{profile.user.username} has logged only {count} BP reading(s) today.",
                notification_type="missed_prescription"
            )
            print(f"⚠️ Notification created for {profile.user.username} — only {count} readings today.")
        else:
            print(f"✅ {profile.user.username} has logged {count} readings today.")

def start():
    """Start the scheduler properly."""
    if not scheduler.running:
        scheduler.add_job(
            check_daily_bp,
            'interval',
            hours=24,
            id="daily_bp_check",
            replace_existing=True
        )
        scheduler.start()
        print("🚀 Scheduler started successfully.")
