import threading
from typing import List, Optional
from core.state_machines import Agent, AgentState

class CallAllocator:
    def __init__(self):
        self._lock = threading.Lock()

    def reserve_agent_atomic(self, agents: List[Agent]) -> Optional[Agent]:
        with self._lock:
            for agent in agents:
                if agent.state == AgentState.AVAILABLE:
                    agent.state = AgentState.RESERVED
                    agent.version += 1
                    return agent
            return None

    def release_agent(self, agent: Agent):
        with self._lock:
            agent.state = AgentState.AVAILABLE
            agent.current_call_id = None
            agent.version += 1