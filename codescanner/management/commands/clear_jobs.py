from django.core.management.base import BaseCommand

from datetime import timedelta
from django.utils import timezone

from codescanner.models import Job

class Command(BaseCommand):

    help = u"Clear all jobs older than 24 hours"

    def handle(self, *args, **options):

        # The delete before date. 30 days from now
        delete_date = timezone.now() - timedelta(days=1)

        # Query for and delete the bookings
        Job.objects.filter(created_date__lte=delete_date).delete()


