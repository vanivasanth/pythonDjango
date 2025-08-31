from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates the required user groups'

    def handle(self, *args, **options):
        Group.objects.get_or_create(name='Manager')
        Group.objects.get_or_create(name='Delivery crew')
        self.stdout.write(self.style.SUCCESS('Successfully created groups'))