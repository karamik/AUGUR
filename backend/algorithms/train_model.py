"""
Скрипт для обучения модели Cognitive Fingerprinting
Запускать только когда есть реальные данные
"""

import numpy as np
import pickle
import os
from real_fingerprint import RealCognitiveFingerprinter

def generate_sample_data():
    """Генерирует пример данных для демонстрации"""
    print("📊 Генерирую пример данных...")
    
    # Создаем данные для 3 агентов
    X = []
    y = []
    
    for agent_id in range(3):
        for _ in range(100):
            # Каждый агент имеет свой "профиль"
            features = np.random.randn(50) + agent_id * 2
            X.append(features)
            y.append(f"agent_{agent_id}")
    
    return np.array(X), np.array(y)

def train():
    """Обучает модель"""
    print("🚀 Начинаю обучение модели...")
    
    # Создаем папку models если её нет
    os.makedirs("../models", exist_ok=True)
    
    # Генерируем данные
    X, y = generate_sample_data()
    print(f"📊 Данные: {X.shape[0]} образцов, {len(np.unique(y))} классов")
    
    # Создаем и обучаем модель
    model = RealCognitiveFingerprinter()
    metrics = model.train(X, y)
    
    print(f"📈 Метрики: {metrics}")
    
    # Сохраняем модель
    model_path = "../models/fingerprint_v1.pkl"
    model.save_model(model_path)
    
    print(f"✅ Модель сохранена в {model_path}")
    print("\n🎉 Готово! Теперь API будет использовать настоящую ML-модель.")

if __name__ == "__main__":
    train()
