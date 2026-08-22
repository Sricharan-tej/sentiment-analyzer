import random
import time
from typing import Dict, Any

class TelecomProviderInterface:
    def initiate_call(self, call_id: str, borrower_id: str) -> Dict[str, Any]:
        raise NotImplementedError

class ProviderA(TelecomProviderInterface):
    def initiate_call(self, call_id: str, borrower_id: str) -> Dict[str, Any]:
        time.sleep(0.01)
        is_success = random.random() < 0.95
        return {
            "provider": "ProviderA",
            "status": "INITIATED" if is_success else "FAILED",
            "events": ["RINGING", "ANSWERED" if random.random() < 0.5 else "FAILED"]
        }

class ProviderB(TelecomProviderInterface):
    def initiate_call(self, call_id: str, borrower_id: str) -> Dict[str, Any]:
        time.sleep(0.05)
        roll = random.random()
        if roll < 0.15:
            return {"provider": "ProviderB", "status": "TIMEOUT", "events": []}
        events = ["RINGING", "ANSWERED", "ANSWERED", "COMPLETED"] if roll < 0.6 else ["COMPLETED", "RINGING"]
        return {"provider": "ProviderB", "status": "INITIATED", "events": events}