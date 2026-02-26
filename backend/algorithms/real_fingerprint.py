"""
REAL Cognitive Fingerprinting™
Настоящий ML-классификатор на базе XGBoost
Обучается различать агентов по поведенческим паттернам
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import pickle
import os
from datetime import datetime, timedelta
from collections import deque
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class RealCognitiveFingerprinter:
    """
    Настоящая ML-реализация Cognitive Fingerprinting
    Использует XGBoost для классификации агентов
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.is_trained = False
        self.confidence_threshold = 0.85
        
        # Загружаем предобученную модель, если есть
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def extract_features(self, events: List[Dict]) -> np.ndarray:
        """
        Извлекает 50+ признаков из последовательности событий
        """
        if len(events) < 20:
            raise ValueError(f"Need at least 20 events, got {len(events)}")
        
        features = {}
        
        # 1. Базовые статистики latency (10 признаков)
        latencies = [e.get('latency_ms', 0) for e in events]
        features['latency_mean'] = np.mean(latencies)
        features['latency_std'] = np.std(latencies)
        features['latency_min'] = np.min(latencies)
        features['latency_max'] = np.max(latencies)
        features['latency_p10'] = np.percentile(latencies, 10)
        features['latency_p25'] = np.percentile(latencies, 25)
        features['latency_p50'] = np.percentile(latencies, 50)
        features['latency_p75'] = np.percentile(latencies, 75)
        features['latency_p90'] = np.percentile(latencies, 90)
        features['latency_p95'] = np.percentile(latencies, 95)
        features['latency_p99'] = np.percentile(latencies, 99)
        
        # 2. Токены (8 признаков)
        tokens = [e.get('tokens_used', 0) for e in events]
        features['tokens_mean'] = np.mean(tokens)
        features['tokens_std'] = np.std(tokens)
        features['tokens_min'] = np.min(tokens)
        features['tokens_max'] = np.max(tokens)
        features['tokens_p25'] = np.percentile(tokens, 25)
        features['tokens_p50'] = np.percentile(tokens, 50)
        features['tokens_p75'] = np.percentile(tokens, 75)
        features['tokens_p90'] = np.percentile(tokens, 90)
        
        # 3. Временные паттерны (12 признаков)
        timestamps = []
        for e in events:
            ts = e.get('timestamp')
            if isinstance(ts, str):
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except:
                    pass
            elif isinstance(ts, datetime):
                timestamps.append(ts)
        
        if timestamps:
            # Интервалы между запросами
            intervals = []
            for i in range(1, len(timestamps)):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(delta)
            
            if intervals:
                features['interval_mean'] = np.mean(intervals)
                features['interval_std'] = np.std(intervals)
                features['interval_min'] = np.min(intervals)
                features['interval_max'] = np.max(intervals)
                features['interval_p50'] = np.percentile(intervals, 50)
                features['interval_p90'] = np.percentile(intervals, 90)
            else:
                for name in ['interval_mean', 'interval_std', 'interval_min', 
                            'interval_max', 'interval_p50', 'interval_p90']:
                    features[name] = 0
            
            # Часы активности
            hours = [ts.hour for ts in timestamps]
            features['hour_mean'] = np.mean(hours)
            features['hour_std'] = np.std(hours)
            features['hour_entropy'] = self._calculate_entropy(hours)
            
            # Дни недели
            days = [ts.weekday() for ts in timestamps]
            features['day_mean'] = np.mean(days)
            features['day_std'] = np.std(days)
            features['day_entropy'] = self._calculate_entropy(days)
        else:
            # Заполняем нулями
            for name in ['interval_mean', 'interval_std', 'interval_min', 'interval_max',
                        'interval_p50', 'interval_p90', 'hour_mean', 'hour_std',
                        'hour_entropy', 'day_mean', 'day_std', 'day_entropy']:
                features[name] = 0
        
        # 4. Типы событий (до 10 признаков)
        event_types = [e.get('event_type', 'unknown') for e in events]
        unique_types = set(event_types)
        for i, et in enumerate(list(unique_types)[:10]):
            features[f'event_type_{i}_freq'] = event_types.count(et) / len(events)
        
        # 5. Ошибки (5 признаков)
        errors = [1 for e in events if e.get('event_type') == 'error']
        features['error_rate'] = len(errors) / len(events)
        features['error_count'] = len(errors)
        
        # Последовательности ошибок
        error_pattern = [1 if e.get('event_type') == 'error' else 0 for e in events]
        features['error_max_consecutive'] = self._max_consecutive(error_pattern)
        features['error_mean_consecutive'] = np.mean([len(list(g)) for k, g in self._groupby(error_pattern) if k == 1]) if errors else 0
        
        # 6. Размеры запросов (5 признаков)
        query_lengths = []
        for e in events:
            query = e.get('data', {}).get('query', '')
            if query:
                query_lengths.append(len(query))
        
        if query_lengths:
            features['query_len_mean'] = np.mean(query_lengths)
            features['query_len_std'] = np.std(query_lengths)
            features['query_len_min'] = np.min(query_lengths)
            features['query_len_max'] = np.max(query_lengths)
            features['query_len_p50'] = np.percentile(query_lengths, 50)
        else:
            for name in ['query_len_mean', 'query_len_std', 'query_len_min',
                        'query_len_max', 'query_len_p50']:
                features[name] = 0
        
        # Преобразуем в вектор фиксированной длины
        feature_vector = []
        self.feature_names = sorted(features.keys())
        for name in self.feature_names:
            feature_vector.append(features.get(name, 0))
        
        return np.array(feature_vector).reshape(1, -1)
    
    def _calculate_entropy(self, values: List[float]) -> float:
        """Вычисляет энтропию распределения"""
        if not values:
            return 0
        _, counts = np.unique(values, return_counts=True)
        probs = counts / len(values)
        return -np.sum(probs * np.log2(probs + 1e-10))
    
    def _max_consecutive(self, arr: List[int]) -> int:
        """Максимальная длина последовательности единиц"""
        max_len = 0
        current = 0
        for x in arr:
            if x == 1:
                current += 1
                max_len = max(max_len, current)
            else:
                current = 0
        return max_len
    
    def _groupby(self, arr: List[int]):
        """Группирует последовательности"""
        from itertools import groupby
        return groupby(arr)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Обучает XGBoost классификатор различать агентов
        X: матрица признаков (n_samples, n_features)
        y: метки агентов (n_samples)
        """
        # Разделяем на train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Масштабируем признаки
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Кодируем метки
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Создаем и обучаем XGBoost
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        
        self.model.fit(
            X_train_scaled, y_train_encoded,
            eval_set=[(X_test_scaled, y_test_encoded)],
            verbose=False
        )
        
        # Оцениваем качество
        train_score = self.model.score(X_train_scaled, y_train_encoded)
        test_score = self.model.score(X_test_scaled, y_test_encoded)
        
        # Предсказания для ROC-AUC (для бинарных задач)
        try:
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            from sklearn.metrics import roc_auc_score
            if len(np.unique(y_test_encoded)) == 2:
                auc = roc_auc_score(y_test_encoded, y_pred_proba[:, 1])
            else:
                auc = roc_auc_score(y_test_encoded, y_pred_proba, multi_class='ovr')
        except:
            auc = 0.0
        
        self.is_trained = True
        
        return {
            'train_accuracy': float(train_score),
            'test_accuracy': float(test_score),
            'roc_auc': float(auc),
            'n_features': X.shape[1],
            'n_classes': len(np.unique(y))
        }
    
    def predict(self, events: List[Dict]) -> Dict[str, Any]:
        """
        Предсказывает, какому агенту принадлежит последовательность
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Извлекаем признаки
        X = self.extract_features(events)
        X_scaled = self.scaler.transform(X)
        
        # Получаем вероятности
        proba = self.model.predict_proba(X_scaled)[0]
        
        # Получаем топ-3 наиболее вероятных агентов
        top_indices = np.argsort(proba)[::-1][:3]
        
        results = []
        for idx in top_indices:
            if proba[idx] > 0.01:  # Отсекаем совсем маловероятные
                agent_class = self.label_encoder.inverse_transform([idx])[0]
                results.append({
                    'agent_class': agent_class,
                    'probability': float(proba[idx])
                })
        
        return {
            'predictions': results,
            'top_prediction': results[0] if results else None,
            'confidence': float(np.max(proba)),
            'is_confident': float(np.max(proba)) > self.confidence_threshold
        }
    
    def compare(self, events_a: List[Dict], events_b: List[Dict]) -> float:
        """
        Сравнивает две последовательности и возвращает вероятность,
        что они от одного агента
        """
        # Извлекаем признаки для обеих последовательностей
        X_a = self.extract_features(events_a)
        X_b = self.extract_features(events_b)
        
        if self.is_trained and self.model is not None:
            # Если есть модель, используем её представления
            X_a_scaled = self.scaler.transform(X_a)
            X_b_scaled = self.scaler.transform(X_b)
            
            # Получаем внутренние представления из дерева решений
            apply_a = self.model.apply(X_a_scaled)
            apply_b = self.model.apply(X_b_scaled)
            
            # Считаем схожесть по листьям
            similarity = np.mean(apply_a == apply_b)
            return float(similarity)
        else:
            # Без модели используем косинусную схожесть признаков
            from scipy.spatial.distance import cosine
            sim = 1 - cosine(X_a.flatten(), X_b.flatten())
            return float(max(0, sim))
    
    def save_model(self, path: str):
        """Сохраняет обученную модель"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Загружает обученную модель"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {path}")


def generate_synthetic_training_data(
    num_agents: int = 5,
    events_per_agent: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Генерирует синтетические данные для обучения
    Каждый агент имеет свой уникальный "профиль" поведения
    """
    from sklearn.datasets import make_classification
    
    # Создаем синтетические данные с 50 признаками
    X, y = make_classification(
        n_samples=num_agents * events_per_agent,
        n_features=50,
        n_informative=30,
        n_redundant=10,
        n_classes=num_agents,
        n_clusters_per_class=2,
        random_state=42
    )
    
    return X, y


# Пример использования
if __name__ == "__main__":
    print("🚀 Training Real Cognitive Fingerprinter...")
    
    # Создаем экземпляр
    fp = RealCognitiveFingerprinter()
    
    # Генерируем синтетические данные для 5 агентов
    X, y = generate_synthetic_training_data(num_agents=5, events_per_agent=1000)
    print(f"Generated dataset: {X.shape} features, {len(np.unique(y))} agents")
    
    # Обучаем модель
    metrics = fp.train(X, y)
    print("\n📊 Training Results:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Сохраняем модель
    fp.save_model("models/fingerprint_v1.pkl")
    print("\n✅ Model saved!")
    
    # Тест на новых данных
    test_events = []  # здесь должны быть реальные события
    print("\n🔮 Ready for predictions!")
