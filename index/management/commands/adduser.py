from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a limited user'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('pass', type=str)

    def handle(self, *args, **options):
        user = User.objects.create_user(options['user'], password=options['pass'])
        user.save()
