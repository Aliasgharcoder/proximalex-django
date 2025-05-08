# user/management/commands/load_fake_lawyers.py
import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from user.models import CustomUser

class Command(BaseCommand):
    help = 'Load fake lawyers from a CSV file'

    def handle(self, *args, **options):
        csv_path = os.path.join('user', 'training_data', 'enhanced_lawyers_data.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_path}"))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['username']
                email = row['email']
                password = row['password']
                specialization = row['specialization']
                sub_specialization = row['sub_specialization']
                experience_years = int(row['experience_years'])
                cases_handled = int(row['cases_handled'])
                location = row['location']
                area = row['area']
                languages_spoken = row['languages_spoken']
                court_experience = row['court_experience']
                hourly_rate = int(row['hourly_rate'])
                success_rate = row['success_rate']
                bio = row['bio']
                is_available = row['is_available'].lower() == 'true'

                if CustomUser.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f"Skipped existing user: {username}"))
                    continue

                CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='lawyer',
                    specialization=specialization,
                    sub_specialization=sub_specialization,
                    experience_years=experience_years,
                    cases_handled=cases_handled,
                    location=location,
                    area=area,
                    languages_spoken=languages_spoken,
                    court_experience=court_experience,
                    hourly_rate=hourly_rate,
                    success_rate=success_rate,
                    bio=bio,
                    is_available=is_available,
                    is_active=True  # This was missing a comma
                )
                self.stdout.write(self.style.SUCCESS(f"Created lawyer: {username}"))

        self.stdout.write(self.style.SUCCESS("🎉 Successfully loaded all fake lawyers!"))