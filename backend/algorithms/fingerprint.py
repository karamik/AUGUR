import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cosine
import hashlib
import json

class CognitiveFingerprinter:
    def __init__(self):
        self.fingerprint_dim = 256
        self.scaler = StandardScaler()
        
    def generate_fingerprint(self, events: List[Dict]) -> Tuple[List[float], float]:
        if len(events) < 10:
            raise ValueError("Need at least 10 events to generate fingerprint")
            
        dimensions = {}
        
        latencies = [e.get('latency_ms', 0) for e in events]
        dimensions['latency'] = [
            float(np.mean(latencies)),
            float(np.percentile(latencies, 50)),
            float(np.percentile(latencies, 95)),
            float(np.percentile(latencies, 99)),
            float(np.std(latencies))
        ]
        
        tokens = [e.get('tokens_used', 0) for e in events]
        dimensions['tokens'] = [
            float(np.mean(tokens)),
            float(np.max(tokens)) if tokens else 0,
            float(np.min(tokens)) if tokens else 0,
            float(np.std(tokens)) if len(tokens) > 1 else 0
        ]
        
        feature_vector = []
        for dim_name, values in dimensions.items():
            if isinstance(values, list):
                feature_vector.extend(values)
            else:
                feature_vector.append(values)
        
        while len(feature_vector) < self.fingerprint_dim:
            feature_vector.append(0.0)
        feature_vector = feature_vector[:self.fingerprint_dim]
        
        feature_vector = np.array(feature_vector, dtype=np.float32)
        if np.std(feature_vector) > 1e-8:
            feature_vector = (feature_vector - np.mean(feature_vector)) / np.std(feature_vector)
        
        confidence = min(99.0, 50 + len(events) * 0.5)
        
        return feature_vector.tolist(), confidence
    
    def compare_fingerprints(self, fp1: List[float], fp2: List[float]) -> float:
        a = np.array(fp1)
        b = np.array(fp2)
        similarity = 1 - cosine(a, b)
        return similarity * 100
    
    def detect_drift(self, fingerprint_history: List[List[float]]) -> Dict[str, Any]:
        if len(fingerprint_history) < 2:
            return {"drift_detected": False, "message": "Not enough history"}
        
        baseline = fingerprint_history[0]
        current = fingerprint_history[-1]
        similarity = self.compare_fingerprints(baseline, current)
        
        similarities = []
        for i in range(1, len(fingerprint_history)):
            sim = self.compare_fingerprints(fingerprint_history[i-1], fingerprint_history[i])
            similarities.append(sim)
        
        drift_rate = float(np.mean(similarities) - similarity) if similarities else 0.0
        
        return {
            "drift_detected": similarity < 85.0,
            "similarity_to_baseline": similarity,
            "drift_rate": drift_rate,
            "stability_score": similarity
        }
