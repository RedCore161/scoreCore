from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Recreates db-schema'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            print("DB cleared!")
