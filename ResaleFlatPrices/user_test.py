import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from tensorflow.keras.models import load_model
# from geopy.distance import geodesic

# ---- Load the Pretrained Model ----
model = load_model('models/hdb_price_prediction_model.h5')

# ---- Load OneHotEncoder and Scaler Used for Preprocessing ----
# You should save these after training your model or retrain them if necessary
ohe = OneHotEncoder(drop='first', sparse_output=False)
scaler = StandardScaler()

# Define the feature columns used in the model
feature_columns = ['floor_area_sqm', 'remaining_lease_months', 'average_storey', 'year', 'month_num', 'distance_to_mrt']

# ---- Function to Process User Input and Predict Price ----
def predict_resale_price(user_input):
    # Step 1: Process the user input (ensure it matches the model's input requirements)
    # Example input: user_input = {'town': 'ANG MO KIO', 'flat_type': '3 ROOM', ...}

    # 1. Encode Categorical Variables
    categorical_cols = ['town', 'flat_type', 'flat_model']
    categorical_input = np.array([user_input[col] for col in categorical_cols]).reshape(1, -1)
    encoded_features = ohe.transform(categorical_input)  # One-hot encode

    # 2. Scale Numerical Features
    numerical_input = np.array([[
        user_input['floor_area_sqm'],
        user_input['remaining_lease_months'],
        user_input['average_storey'],
        user_input['year'],
        user_input['month_num'],
        user_input['distance_to_mrt']
    ]])

    scaled_features = scaler.transform(numerical_input)  # Standardize numerical features

    # 3. Combine the encoded and scaled features
    processed_input = np.concatenate([encoded_features, scaled_features], axis=1)

    # Step 2: Predict the resale price using the trained model
    predicted_price = model.predict(processed_input)
    return predicted_price[0][0]  # Return the predicted price

# ---- User Input ----
user_input = {
    'town': 'ANG MO KIO',
    'flat_type': '3 ROOM',
    'flat_model': 'New Generation',
    'floor_area_sqm': 67,
    'remaining_lease_months': 720,  # Example: 60 years * 12 months = 720 months
    'average_storey': 5,  # Example: Average of 4 to 6 storey range
    'year': 1980,
    'month_num': 1,
    'distance_to_mrt': 1.2  # Example: Distance in km to the nearest MRT station
}

# ---- Get Prediction ----
predicted_price = predict_resale_price(user_input)
print(f"The estimated resale price of the house is: SGD {predicted_price:,.2f}")