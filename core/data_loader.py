import csv
import os
from typing import List, Tuple

class DatasetLoader:
    def __init__(self, data_dir: str = "collections_30k_dataset"):
        self.data_dir = data_dir

    def load_agents(self) -> List[str]:
        agents = []
        path = os.path.join(self.data_dir, "agents.csv")
        if os.path.exists(path):
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    agent_id = row.get("agent_id") or row.get("id")
                    if agent_id:
                        agents.append(agent_id)
        return agents if agents else [f"agent_{i}" for i in range(50)]

    def load_target_borrowers(self) -> List[str]:
        borrowers = []
        target_path = os.path.join(self.data_dir, "daily_targeting.csv")
        borrower_path = os.path.join(self.data_dir, "borrowers.csv")
        
        target_file = target_path if os.path.exists(target_path) else borrower_path
        if os.path.exists(target_file):
            with open(target_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    b_id = row.get("borrower_id") or row.get("account_id") or row.get("id")
                    if b_id:
                        borrowers.append(b_id)
        return borrowers if borrowers else [f"borrower_{i}" for i in range(1000)]

    def compute_historical_pacing_stats(self) -> Tuple[float, float]:
        attempts_path = os.path.join(self.data_dir, "call_attempts.csv")
        calls_path = os.path.join(self.data_dir, "calls.csv")
        
        total_calls = 0
        connected_calls = 0
        total_duration = 0.0

        target_file = calls_path if os.path.exists(calls_path) else attempts_path
        if os.path.exists(target_file):
            with open(target_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_calls += 1
                    status = str(row.get("disposition") or row.get("status") or "").upper()
                    duration = float(row.get("duration") or row.get("talk_time") or 0.0)
                    
                    if status in {"CONNECTED", "ANSWERED", "COMPLETED"} or duration > 0:
                        connected_calls += 1
                        total_duration += duration

        answer_rate = (connected_calls / total_calls) if total_calls > 0 else 0.35
        avg_talk_time = (total_duration / connected_calls) if connected_calls > 0 else 90.0
        
        return round(max(0.10, min(answer_rate, 0.90)), 2), round(max(30.0, avg_talk_time), 1)