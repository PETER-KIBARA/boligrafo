from django.core.management.base import BaseCommand
from postd.services import NotificationService

class Command(BaseCommand):
    help = 'Generate notifications for missed prescriptions and critical BP readings'

    def handle(self, *args, **options):
        self.stdout.write('Generating notifications...')
        NotificationService.generate_all_notifications()
        self.stdout.write(
            self.style.SUCCESS('Successfully generated notifications')
        )