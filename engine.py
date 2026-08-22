import uuid
import time
from typing import List, Dict
from core.state_machines import Agent, AgentState, Call, CallState, CallStateMachine
from core.pacing_engine import ProgressivePacingEngine, PredictivePacingEngine
from core.safety_controller import SafetyController
from core.call_allocator import CallAllocator
from core.mock_providers import ProviderA, ProviderB

class SmartDialer:
    def __init__(self, mode: str = "PREDICTIVE"):
        self.mode = mode
        self.pacing_engine = PredictivePacingEngine() if mode == "PREDICTIVE" else ProgressivePacingEngine()
        self.safety_controller = SafetyController()
        self.allocator = CallAllocator()
        self.provider = ProviderA()
        
        self.agents: Dict[str, Agent] = {}
        self.borrower_queue: List[str] = [f"borrower_{i}" for i in range(1000)]
        self.active_calls: Dict[str, Call] = {}
        
        self.metrics = {
            "pacing_requested": 0,
            "safety_approved": 0,
            "calls_initiated": 0,
            "calls_connected": 0,
            "abandoned_calls": 0,
            "provider_failures": 0
        }

    def register_agent(self, agent_id: str):
        self.agents[agent_id] = Agent(agent_id=agent_id)

    def run_cycle(self, answer_rate: float = 0.4, avg_talk_time: float = 90.0):
        avail_agents = sum(1 for a in self.agents.values() if a.state == AgentState.AVAILABLE)
        connected_calls = sum(1 for c in self.active_calls.values() if c.state == CallState.CONNECTED)
        ringing_calls = sum(1 for c in self.active_calls.values() if c.state in {CallState.INITIATED, CallState.RINGING})
        
        context = {
            "mode": self.mode,
            "available_agents": avail_agents,
            "active_calls": connected_calls,
            "ringing_calls": ringing_calls,
            "avg_talk_time": avg_talk_time,
            "historical_answer_rate": answer_rate,
            "provider_health": 1.0 - (self.safety_controller.consecutive_provider_failures * 0.15)
        }

        raw_dials = self.pacing_engine.calculate_dials(context)
        self.metrics["pacing_requested"] += raw_dials

        approved_dials = self.safety_controller.evaluate(raw_dials, context)
        self.metrics["safety_approved"] += approved_dials

        for _ in range(approved_dials):
            if not self.borrower_queue:
                break
            borrower_id = self.borrower_queue.pop(0)
            call_id = str(uuid.uuid4())[:8]
            call = Call(call_id=call_id, borrower_id=borrower_id)
            self.active_calls[call_id] = call
            
            CallStateMachine.transition(call, CallState.INITIATED)
            self.metrics["calls_initiated"] += 1
            
            res = self.provider.initiate_call(call_id, borrower_id)
            if res["status"] in {"FAILED", "TIMEOUT"}:
                CallStateMachine.transition(call, CallState.FAILED)
                self.safety_controller.record_provider_result(False)
                self.metrics["provider_failures"] += 1
                continue
            
            self.safety_controller.record_provider_result(True)

            for event_name in res["events"]:
                target_state = CallState[event_name]
                if target_state == CallState.ANSWERED:
                    reserved_agent = self.allocator.reserve_agent_atomic(list(self.agents.values()))
                    if reserved_agent:
                        reserved_agent.current_call_id = call_id
                        reserved_agent.state = AgentState.CONNECTED
                        call.agent_id = reserved_agent.agent_id
                        CallStateMachine.transition(call, CallState.CONNECTED)
                        self.metrics["calls_connected"] += 1
                    else:
                        CallStateMachine.transition(call, CallState.FAILED)
                        self.metrics["abandoned_calls"] += 1
                else:
                    CallStateMachine.transition(call, target_state)