import math
from typing import Dict, Any

class BasePacingEngine:
    def calculate_dials(self, context: Dict[str, Any]) -> int:
        raise NotImplementedError

class ProgressivePacingEngine(BasePacingEngine):
    def calculate_dials(self, context: Dict[str, Any]) -> int:
        return max(0, context.get("available_agents", 0))

class PredictivePacingEngine(BasePacingEngine):
    def calculate_dials(self, context: Dict[str, Any]) -> int:
        available_agents = context.get("available_agents", 0)
        active_calls = context.get("active_calls", 0)
        avg_talk_time = max(context.get("avg_talk_time", 90.0), 1.0)
        pacing_interval = context.get("pacing_interval", 5.0)
        answer_rate = max(min(context.get("historical_answer_rate", 0.3), 0.95), 0.05)
        
        expected_free_agents = active_calls * (pacing_interval / avg_talk_time)
        context["expected_free_agents"] = int(math.floor(expected_free_agents))
        
        total_target_agents = available_agents + expected_free_agents
        raw_dials = math.floor(total_target_agents / answer_rate)
        return int(max(0, raw_dials))