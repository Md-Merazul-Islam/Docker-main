from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Check if superuser is correctly set'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        try:
            user = User.objects.get(username='admin')  # Replace with your superuser username
            self.stdout.write(f'Superuser: {user.email}, is_superuser: {user.is_superuser}, is_staff: {user.is_staff}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User does not exist'))
