# user/management/commands/generate_training_data.py
import csv
import random
import os
from django.core.management.base import BaseCommand
from user.models import CustomUser

class Command(BaseCommand):
    help = 'Generate enhanced training data for lawyer-case matching'

    def handle(self, *args, **kwargs):
        lawyers = CustomUser.objects.filter(role='lawyer')
        if not lawyers.exists():
            self.stdout.write(self.style.ERROR("No lawyers found in database!"))
            return

        case_types = {
            "Criminal Law": ["Drug Offenses", "Violent Crimes", "White Collar Crimes"],
            "Family Law": ["Divorce", "Child Custody", "Adoption"],
            "Corporate Law": ["Mergers", "Contracts", "Compliance"],
            "Immigration Law": ["Visas", "Citizenship", "Deportation"],
            "Property Law": ["Land Disputes", "Rental Issues"]
        }

        save_path = os.path.join('user', 'training_data', 'enhanced_training_data.csv')

        with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'specialization', 'sub_specialization', 'years_of_experience',
                'location', 'area', 'hourly_rate', 'success_rate',
                'cases_handled', 'court_experience', 'languages_spoken',
                'case_type', 'case_subtype', 'case_urgency', 'case_complexity',
                'label_lawyer_id', 'match_score'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for lawyer in lawyers:
                for _ in range(random.randint(5, 20)):  # 5-20 cases per lawyer
                    if lawyer.specialization not in case_types:
                        continue

                    case_subtype = random.choice(case_types[lawyer.specialization])
                    match_score = random.uniform(0.7, 1.0)  # Base match score
                    
                    # Adjust score based on experience
                    match_score *= min(1.0, 0.7 + (lawyer.experience_years / 40))
                    
                    # Adjust score based on success rate
                    if lawyer.success_rate:
                        sr = float(lawyer.success_rate.strip('%'))
                        match_score *= min(1.0, 0.7 + (sr / 100))

                    writer.writerow({
                        'specialization': lawyer.specialization,
                        'sub_specialization': lawyer.sub_specialization,
                        'years_of_experience': lawyer.experience_years,
                        'location': lawyer.location,
                        'area': lawyer.area,
                        'hourly_rate': lawyer.hourly_rate,
                        'success_rate': lawyer.success_rate,
                        'cases_handled': lawyer.cases_handled,
                        'court_experience': lawyer.court_experience,
                        'languages_spoken': lawyer.languages_spoken,
                        'case_type': lawyer.specialization,  # Case matches lawyer's specialization
                        'case_subtype': case_subtype,
                        'case_urgency': random.choice(['Low', 'Medium', 'High']),
                        'case_complexity': random.choice(['Simple', 'Moderate', 'Complex']),
                        'label_lawyer_id': lawyer.id,
                        'match_score': round(match_score, 2)
                    })

        self.stdout.write(self.style.SUCCESS(f'✅ Generated enhanced training data at {save_path}'))