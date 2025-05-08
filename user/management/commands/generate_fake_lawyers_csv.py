# user/management/commands/generate_fake_lawyers_csv.py
from django.core.management.base import BaseCommand
import csv
import random
import os
from faker import Faker

class Command(BaseCommand):
    help = 'Generate a CSV file with realistic fake lawyers for case matching'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Enhanced legal specializations with sub-categories
        specializations = {
            "Criminal Law": ["Drug Offenses", "Violent Crimes", "White Collar Crimes"],
            "Family Law": ["Divorce", "Child Custody", "Adoption"],
            "Corporate Law": ["Mergers", "Contracts", "Compliance"],
            "Civil Rights": ["Discrimination", "Police Brutality"],
            "Immigration Law": ["Visas", "Citizenship", "Deportation"],
            "Intellectual Property": ["Patents", "Copyright", "Trademarks"],
            "Property Law": ["Land Disputes", "Rental Issues"]
        }
        
        # Pakistani cities with legal hubs
        locations = {
            "Karachi": ["Clifton", "Saddar", "Defence"],
            "Lahore": ["Gulberg", "Model Town", "DHA"],
            "Islamabad": ["F-8", "G-11", "Blue Area"],
            "Peshawar": ["University Town", "Hayatabad"],
            "Quetta": ["Jinnah Town", "Samungli Road"]
        }
        
        # Languages with proficiency levels
        languages = ["English (Fluent)", "Urdu (Native)", "Punjabi (Conversational)", 
                    "Sindhi (Basic)", "Pashto (Conversational)"]
        
        # Court experience levels
        court_experience = ["High Court", "District Court", "Session Court", "Special Tribunals"]
        
        save_path = os.path.join('user', 'training_data', 'enhanced_lawyers_data.csv')

        with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'username', 'email', 'password', 
                'specialization', 'sub_specialization', 
                'experience_years', 'cases_handled',
                'location', 'area', 
                'languages_spoken', 'court_experience',
                'hourly_rate', 'success_rate',
                'bio', 'is_available'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(1, 101):
                # Select specialization and sub-specialization
                spec = random.choice(list(specializations.keys()))
                sub_spec = random.choice(specializations[spec])
                
                # Select location and area
                city = random.choice(list(locations.keys()))
                area = random.choice(locations[city])
                
                # Generate realistic data
                exp_years = random.randint(1, 25)
                cases_handled = random.randint(10, 500)
                hourly_rate = random.randint(2000, 20000)
                success_rate = random.randint(60, 95)
                
                writer.writerow({
                    'username': f'lawyer_{fake.user_name()}',
                    'email': f'lawyer_{i}@{fake.domain_name()}',
                    'password': 'defaultpassword123',
                    'specialization': spec,
                    'sub_specialization': sub_spec,
                    'experience_years': exp_years,
                    'cases_handled': cases_handled,
                    'location': city,
                    'area': area,
                    'languages_spoken': ', '.join(random.sample(languages, random.randint(2, 4))),
                    'court_experience': ', '.join(random.sample(court_experience, random.randint(1, 3))),
                    'hourly_rate': hourly_rate,
                    'success_rate': f"{success_rate}%",
                    'bio': f"{fake.text(max_nb_chars=200)}\n\nSpecializing in {sub_spec.lower()} cases in {city}. "
                          f"Handled {cases_handled}+ cases with {success_rate}% success rate.",
                    'is_available': random.choice([True, False])
                })

        self.stdout.write(self.style.SUCCESS('✅ Generated 100 enhanced lawyer profiles for case matching!'))