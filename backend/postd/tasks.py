from celery import shared_task
from .services import NotificationService

@shared_task
def generate_notifications_task():
    NotificationService.generate_all_notifications()