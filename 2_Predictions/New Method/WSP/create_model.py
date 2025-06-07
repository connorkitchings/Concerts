import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib
from prepare_data import prepare_model_data

MODEL_PATH = 'setlist_model.joblib'

def create_model():
    # Prepare data
    df = prepare_model_data()
    
    # Select features and target (all are positive samples)
    features = ['year', 'month', 'weekday', 'venue', 'city', 'state', 'ftp', 'ltp', 'times_played']
    X = df[features].copy()
    y = pd.Series(1, index=df.index)  # All rows are positive (song played at show)

    # Encode categorical features
    categorical = ['venue', 'city', 'state', 'weekday']
    X = pd.get_dummies(X, columns=categorical)

    # Train/test split (optional, for evaluation)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")
    return model

if __name__ == '__main__':
    create_model()
