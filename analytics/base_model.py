from abc import ABC, abstractmethod
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
from pathlib import Path

class BaseMLModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_trained = False
    
    @abstractmethod
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        pass
    
    @abstractmethod
    def build_model(self):
        pass
    
    def train(self, df: pd.DataFrame, target_column: str):
        X, y = self.prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = self.build_model()
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        predictions = self.model.predict(X_test)
        return self.evaluate(y_test, predictions)
    
    def predict(self, df: pd.DataFrame):
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X, _ = self.prepare_features(df)
        return self.model.predict(X)
    
    def save_model(self):
        model_path = Path("analytics/ml_models") / f"{self.model_name}.joblib"
        joblib.dump(self.model, model_path)
    
    @abstractmethod
    def evaluate(self, y_true, y_pred):
        pass