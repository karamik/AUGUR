import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

class ConflictPredictor:
    def __init__(self):
        self.conflict_threshold = 0.7
        self.prediction_horizon = 24
        
    def predict_conflicts(self, agents: List[Dict], recent_events: Dict[str, List[Dict]]) -> List[Dict]:
        predictions = []
        
        for i, agent_a in enumerate(agents):
            for j, agent_b in enumerate(agents):
                if i >= j:
                    continue
                    
                events_a = recent_events.get(agent_a['id'], [])
                events_b = recent_events.get(agent_b['id'], [])
                
                if len(events_a) < 5 or len(events_b) < 5:
                    continue
                
                probability = self._calculate_conflict_probability(events_a, events_b)
                
                if probability > self.conflict_threshold:
                    conflict_type = self._determine_conflict_type()
                    severity = self._determine_severity(probability)
                    predicted_time = datetime.utcnow() + timedelta(
                        hours=np.random.randint(1, self.prediction_horizon)
                    )
                    
                    predictions.append({
                        "agent_a_id": agent_a['id'],
                        "agent_b_id": agent_b['id'],
                        "probability": float(probability),
                        "conflict_type": conflict_type,
                        "predicted_time": predicted_time.isoformat(),
                        "severity": severity
                    })
        
        return predictions
    
    def _calculate_conflict_probability(self, events_a: List[Dict], events_b: List[Dict]) -> float:
        interaction_count = 0
        for ea in events_a[-20:]:
            for eb in events_b[-20:]:
                time_diff = abs((datetime.fromisoformat(ea['timestamp']) - datetime.fromisoformat(eb['timestamp'])).total_seconds()) if isinstance(ea.get('timestamp'), str) else 0
                if time_diff < 60:
                    interaction_count += 1
        
        interaction_prob = min(1.0, interaction_count / 5)
        
        activity_a = len(events_a)
        activity_b = len(events_b)
        peak_factor = min(1.0, (activity_a + activity_b) / 100)
        
        probability = 0.6 * interaction_prob + 0.4 * peak_factor
        return float(min(0.99, probability))
    
    def _determine_conflict_type(self) -> str:
        types = ["resource_contention", "goal_misalignment", "priority_conflict"]
        return str(np.random.choice(types))
    
    def _determine_severity(self, probability: float) -> str:
        if probability > 0.9:
            return "critical"
        elif probability > 0.8:
            return "high"
        elif probability > 0.7:
            return "medium"
        else:
            return "low"
    
    def suggest_resolution(self, conflict: Dict) -> Dict:
        strategies = {
            "resource_contention": "caching",
            "goal_misalignment": "negotiation",
            "priority_conflict": "time_slicing"
        }
        
        strategy = strategies.get(conflict.get('conflict_type', ''), "defer")
        
        return {
            "conflict_id": conflict.get('id', ''),
            "recommended_strategy": strategy,
            "estimated_impact": f"~${np.random.randint(1000, 5000)} savings",
            "auto_resolvable": conflict.get('probability', 0) < 0.95
        }
