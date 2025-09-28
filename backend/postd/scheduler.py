# import logging
# from datetime import timedelta
# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events
# from django.db.utils import OperationalError, ProgrammingError
# from django.utils import timezone
# from .models import VitalReading, Prescription, Notification


# logger = logging.getLogger(__name__)

# def check_notifications():
#     """
#     Runs periodically to check:
#     1. Abnormal vital readings
#     2. Missing today's vitals
#     3. Missed prescriptions
#     Creates Notification objects for doctors.
#     """
#     now = timezone.now().date()

#     # 1. Abnormal vitals
#     abnormal_vitals = VitalReading.objects.filter(
#         systolic__gt=140
#     ) | VitalReading.objects.filter(
#         diastolic__gt=90
#     )
#     for vital in abnormal_vitals:
#         Notification.objects.get_or_create(
#             doctor=vital.patient.doctor,   # ✅ doctor comes from UserProfile
#             patient=vital.patient.user,    # ✅ still keep the raw User for clarity
#             message=f"Abnormal vitals for {vital.patient.user.username}: "
#                     f"{vital.systolic}/{vital.diastolic}",
#         )

#     # 2. Missing today's vitals
#     patients = Prescription.objects.values_list("patient", flat=True).distinct()
#     for patient_id in patients:
#         if not VitalReading.objects.filter(patient_id=patient_id, created_at__date=now).exists():
#             Notification.objects.get_or_create(
#                 doctor=None,  # optional: notify doctor
#                 patient_id=patient_id,
#                 message="Patient has not entered vitals today.",
#             )

#     # 3. Missed prescriptions (where taken=False & due date < today)
#     missed = Prescription.objects.filter(taken=False, end_date__lt=now)
#     for p in missed:
#         Notification.objects.get_or_create(
#             doctor=p.doctor,
#             patient=p.patient,
#             message=f"Missed dose: {p.medication}",
#         )

# def start():
#     """Start the scheduler and register the notification checker."""
#     try:
#         scheduler = BackgroundScheduler(timezone="UTC")
#         scheduler.add_jobstore(DjangoJobStore(), "default")

#         scheduler.add_job(
#             check_notifications,
#             trigger="interval",
#             minutes=5,  # every 5 minutes
#             id="check_notifications",
#             replace_existing=True,
#         )

#         register_events(scheduler)
#         scheduler.start()
#         logger.info("✅ Scheduler started: checking notifications every 5 minutes")

#     except (OperationalError, ProgrammingError):
#         # Happens before migrations are applied
#         logger.warning("Scheduler skipped - database not ready yet.")
