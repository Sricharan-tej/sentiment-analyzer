from typing import Dict, Any

class SafetyController:
    def __init__(self, max_abandonment_rate: float = 0.03, min_provider_health: float = 0.60):
        self.max_abandonment_rate = max_abandonment_rate
        self.min_provider_health = min_provider_health
        self.consecutive_provider_failures = 0

    def evaluate(self, proposed_dials: int, context: Dict[str, Any]) -> int:
        available_agents = context.get("available_agents", 0)
        expected_free_agents = context.get("expected_free_agents", 0)
        ringing_calls = context.get("ringing_calls", 0)
        provider_health = context.get("provider_health", 1.0)
        mode = context.get("mode", "PROGRESSIVE")

        if provider_health < self.min_provider_health or self.consecutive_provider_failures >= 5:
            return 0

        if mode == "PROGRESSIVE":
            allowed = max(0, available_agents - ringing_calls)
            return min(proposed_dials, allowed)

        total_projected_capacity = available_agents + expected_free_agents
        max_allowable_in_flight = int(total_projected_capacity * 1.5)
        
        permitted_dials = max(0, max_allowable_in_flight - ringing_calls)
        approved_dials = min(proposed_dials, permitted_dials)

        if available_agents == 0 and expected_free_agents == 0:
            return 0

        return approved_dials

    def record_provider_result(self, success: bool):
        if not success:
            self.consecutive_provider_failures += 1
        else:
            self.consecutive_provider_failures = max(0, self.consecutive_provider_failures - 1)