# user/management/commands/train_model.py
from django.core.management.base import BaseCommand
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import joblib
import os
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class Command(BaseCommand):
    help = 'Train the lawyer matching model'
    
    def handle(self, *args, **options):
        try:
            # Get paths
            BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
            csv_path = os.path.join(BASE_DIR, 'user', 'training_data', 'enhanced_training_data.csv')
            model_dir = os.path.join(BASE_DIR, 'user', 'lawyer_matcher')
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, 'xgboost_model.pkl')
            
            # Load data
            self.stdout.write("Loading training data...")
            df = pd.read_csv(csv_path)
            if df['success_rate'].dtype == object:
               df['success_rate'] = df['success_rate'].str.rstrip('%').astype(float)
            # Feature engineering
            df['experience_bucket'] = pd.cut(
                df['years_of_experience'],
                bins=[0, 5, 10, 15, 20, 30, 50],
                labels=['0-5', '5-10', '10-15', '15-20', '20-30', '30+']
            )
            
            # Define features
            categorical_features = [
                'specialization', 'sub_specialization', 'location', 'area',
                'court_experience', 'case_type', 'case_subtype',
                'case_urgency', 'case_complexity', 'experience_bucket'
            ]
            
            numerical_features = [
                'years_of_experience', 'hourly_rate',
                'cases_handled', 'success_rate'
            ]
            
            # Preprocessing
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', 'passthrough', numerical_features),
                    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
                ])
            
            # Model pipeline
            model = xgb.XGBRegressor(
                objective='reg:squarederror',
                n_estimators=500,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            
            pipeline = Pipeline([
                ('preprocessor', preprocessor),
                ('model', model)
            ])
            
            # Train model
            self.stdout.write("Training model...")
            X = df[categorical_features + numerical_features]
            y = df['match_score']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            pipeline.fit(X_train, y_train)
            
            # Evaluate
            y_pred = pipeline.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            self.stdout.write(self.style.SUCCESS(f"Model RMSE: {rmse:.4f}"))
            
            # Save model
            joblib.dump(pipeline, model_path)
            self.stdout.write(self.style.SUCCESS(f"✅ Model saved to {model_path}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            raise e