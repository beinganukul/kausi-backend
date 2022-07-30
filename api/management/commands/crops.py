import json
from api.models import Crop 
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Upload Crop from json"

    def add_arguments(self, parser):
        parser.add_argument("populate_db")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            with open("crops.json", 'r') as fh:
                crop_data = json.load(fh)      
            for crop in crop_data:
                Crop.objects.create(**crop)
            self.stdout.write(self.style.SUCCESS("Crop Data Successfully Inserted"))
        except:
            raise CommandError("There may be some fault in Crop data")
