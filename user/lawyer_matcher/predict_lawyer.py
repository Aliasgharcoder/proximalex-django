# user/lawyer_matcher/predict_lawyer.py
# user/lawyer_matcher/predict_lawyer.py
import joblib
import os
import pandas as pd
from django.contrib.auth import get_user_model
import random

User = get_user_model()

# Load model once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pipeline = joblib.load(os.path.join(BASE_DIR, 'xgboost_model.pkl'))

def get_experience_bucket(years):
    if years <= 5: return '0-5'
    elif years <= 10: return '5-10'
    elif years <= 15: return '10-15'
    elif years <= 20: return '15-20'
    elif years <= 30: return '20-30'
    else: return '30+'


def predict_best_lawyers(case_details, top_n=5):
    """
    Predict best lawyers for a case with improved diversity
    
    Args:
        case_details: {
            'case_type': str,
            'case_subtype': str,
            'location': str,
            'urgency': str,
            'complexity': str,
            'max_hourly_rate': int (optional)
        }
        top_n: Number of lawyers to return
        
    Returns:
        List of lawyers sorted by score with diversity
    """
    print("\nInput case details:", case_details)

    try:
        # Get available lawyers with required fields
        lawyers = User.objects.filter(
            role='lawyer',
            is_available=True,
            experience_years__isnull=False,
            specialization__isnull=False
        ).exclude(specialization='')
        
        if not lawyers.exists():
            return []
        
        # Prepare case data with proper null checks
        cases = []
        valid_lawyers = []
        
        for lawyer in lawyers:
            try:
                cases.append({
                    'specialization': lawyer.specialization.lower() if lawyer.specialization else 'unknown',
                    'sub_specialization': (lawyer.sub_specialization or 'general').lower(),
                    'years_of_experience': lawyer.experience_years,
                    'location': (lawyer.location or 'unknown').lower(),
                    'area': (lawyer.area or 'unknown').lower() if hasattr(lawyer, 'area') else 'unknown',
                    'hourly_rate': lawyer.hourly_rate or 0,
                    'success_rate': float(lawyer.success_rate.strip('%')) if lawyer.success_rate else 70,
                    'cases_handled': lawyer.cases_handled or 0,
                    'court_experience': (lawyer.court_experience or 'none').lower() if hasattr(lawyer, 'court_experience') else 'none',
                    'case_type': case_details.get('case_type', 'unknown').lower(),
                    'case_subtype': case_details.get('case_subtype', 'general').lower(),
                    'case_urgency': case_details.get('urgency', 'medium').lower(),
                    'case_complexity': case_details.get('complexity', 'medium').lower(),
                    'experience_bucket': get_experience_bucket(lawyer.experience_years)
                })
                valid_lawyers.append(lawyer)
            except AttributeError as e:
                print(f"Skipping lawyer {lawyer.id} due to missing attribute: {e}")
                continue
        
        if not cases:
            return []
        
        # Get predictions
        df = pd.DataFrame(cases)
        scores = pipeline.predict(df)
        
        # Combine results with proper error handling
        results = []
        max_rate = case_details.get('max_hourly_rate')
        
        for i, (lawyer, score) in enumerate(zip(valid_lawyers, scores)):
            try:
                # Skip if exceeds max hourly rate
                if max_rate and lawyer.hourly_rate and lawyer.hourly_rate > float(max_rate):
                    continue
                         
                 # Calculate additional matching factors
                specialization_match = 1 if lawyer.specialization.lower() == case_details.get('case_type', '').lower() else 0
                location_match = 1 if lawyer.location and case_details.get('location') and lawyer.location.lower() == case_details['location'].lower() else 0
                results.append({
                    'lawyer': lawyer,
                    'score': score,
                    'hourly_rate': lawyer.hourly_rate or 0,
                    'specialization_match': 1 if lawyer.specialization and case_details.get('case_type') and lawyer.specialization.lower() == case_details['case_type'].lower() else 0,
                    'location_match': 1 if lawyer.location and case_details.get('location') and lawyer.location.lower() == case_details['location'].lower() else 0,
                    'experience': lawyer.experience_years or 0
                })
            except Exception as e:
                print(f"Error processing lawyer {lawyer.id}: {e}")
                continue
        
        if not results:
            return []
        
        # Sort with multiple factors
        results.sort(
            key=lambda x: (
                -x['score'],
                -x['specialization_match'],
                -x['location_match'],
                x['hourly_rate'],
                -x['experience']
            )
        )
        print("First 5 raw scores:", scores[:5])
        # Add this right after prediction
        # Debug: Inspect your pipeline structure
        print("\n=== Pipeline Structure ===")
        print("Pipeline steps:", pipeline.named_steps.keys() if hasattr(pipeline, 'named_steps') else pipeline.steps)
        
        # Get predictions
        df = pd.DataFrame(cases)
        scores = pipeline.predict(df)
        print("First 5 raw scores:", scores[:5])
        
        # Get feature importance if available
        if hasattr(pipeline, 'named_steps'):
            # If using named steps
            final_step = list(pipeline.named_steps.keys())[-1]
            final_estimator = pipeline.named_steps[final_step]
        else:
            # If using unnamed steps
            final_estimator = pipeline.steps[-1][1]
        
        if hasattr(final_estimator, 'feature_importances_'):
            try:
                feature_names = pipeline[:-1].get_feature_names_out()
                importances = final_estimator.feature_importances_
                print("\nFeature Importances:")
                for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
                    print(f"{name}: {imp:.4f}")
            except Exception as e:
                print(f"Couldn't get feature names: {e}")
        else:
            print("Final estimator has no feature_importances_ attribute")
            # Return top results
        return [(r['lawyer'],r['score']) for r in results[:top_n]]
        
    except Exception as e:
        print(f"Error in predict_best_lawyers: {e}")
        return []
