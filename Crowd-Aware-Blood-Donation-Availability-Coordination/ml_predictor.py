
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class BloodDemandPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def generate_synthetic_data(self, days=365):
        """Generates synthetic historical data with trends"""
        data = []
        start_date = datetime.now() - timedelta(days=days)
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            # Seasonality: More demand in monsoon (June-Aug) and Dengue season (Sep-Nov)
            month = current_date.month
            base_demand = np.random.randint(5, 15)
            
            if 6 <= month <= 11:
                base_demand += np.random.randint(5, 10) # Higher demand
                
            for bg in blood_groups:
                # O+ and B+ are more common, so higher demand
                modifier = 1.5 if bg in ['O+', 'B+'] else 1.0
                demand = int(np.random.normal(base_demand * modifier, 2))
                data.append({
                    'date': current_date,
                    'day_of_year': current_date.timetuple().tm_yday,
                    'month': month,
                    'weekday': current_date.weekday(),
                    'blood_group': bg,
                    'demand': max(0, demand) # Demand can't be negative
                })
                
        return pd.DataFrame(data)

    def train(self):
        """Trains the model on synthetic data"""
        df = self.generate_synthetic_data()
        
        # Encoding Blood Group
        df_encoded = pd.get_dummies(df, columns=['blood_group'], prefix='bg')
        
        # Features: Day of Year, Month, Weekday, One-Hot Blood Groups
        X = df_encoded.drop(['date', 'demand'], axis=1)
        y = df['demand']
        
        self.model.fit(X, y)
        self.is_trained = True
        self.feature_columns = X.columns
        print("Model trained successfully.")

    def predict_next_week_demand(self):
        """Predicts demand for all blood groups for the next 7 days"""
        if not self.is_trained:
            self.train()
            
        predictions = {}
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        next_week = [datetime.now() + timedelta(days=i) for i in range(1, 8)]
        
        for bg in blood_groups:
            total_predicted_demand = 0
            for date in next_week:
                # Prepare input vector (must match training features)
                input_data = {
                    'day_of_year': date.timetuple().tm_yday,
                    'month': date.month,
                    'weekday': date.weekday()
                }
                
                # Add blood group dummy variables
                for g in blood_groups:
                    input_data[f'bg_{g}'] = 1 if g == bg else 0
                    
                # Create DataFrame for prediction to ensure column order matches (if using pandas < 1.0 or depending on config, but dict-to-df is safer with reindexing if needed)
                # Simpler: Create a single row DF with all columns initialized to 0 then set values
                input_df = pd.DataFrame([input_data])
                
                # Align columns with training data (add missing columns with 0 if any)
                for col in self.feature_columns:
                    if col not in input_df.columns:
                        input_df[col] = 0
                
                # Reorder columns to match training
                input_df = input_df[self.feature_columns]
                
                prediction = self.model.predict(input_df)[0]
                total_predicted_demand += prediction
                
            predictions[bg] = int(total_predicted_demand)
            
        return predictions

# Singleton instance
predictor = BloodDemandPredictor()
