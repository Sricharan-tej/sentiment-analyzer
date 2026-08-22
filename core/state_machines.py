import enum
import time
from dataclasses import dataclass, field
from typing import Optional

class AgentState(enum.Enum):
    OFFLINE = "OFFLINE"
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    DIALING = "DIALING"
    CONNECTED = "CONNECTED"
    WRAP_UP = "WRAP_UP"
    PAUSED = "PAUSED"

class CallState(enum.Enum):
    QUEUED = 0
    RESERVED = 1
    INITIATED = 2
    RINGING = 3
    ANSWERED = 4
    CONNECTED = 5
    COMPLETED = 6
    FAILED = 7
    CANCELLED = 8

TERMINAL_CALL_STATES = {CallState.COMPLETED, CallState.FAILED, CallState.CANCELLED}

@dataclass
class Agent:
    agent_id: str
    state: AgentState = AgentState.AVAILABLE
    current_call_id: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    version: int = 0

@dataclass
class Call:
    call_id: str
    borrower_id: str
    agent_id: Optional[str] = None
    state: CallState = CallState.QUEUED
    state_seq: int = 0
    created_at: float = field(default_factory=time.time)
    answered_at: Optional[float] = None
    provider_id: Optional[str] = None

class CallStateMachine:
    VALID_TRANSITIONS = {
        CallState.QUEUED: {CallState.RESERVED, CallState.CANCELLED},
        CallState.RESERVED: {CallState.INITIATED, CallState.FAILED, CallState.CANCELLED},
        CallState.INITIATED: {CallState.RINGING, CallState.ANSWERED, CallState.FAILED, CallState.CANCELLED},
        CallState.RINGING: {CallState.ANSWERED, CallState.FAILED, CallState.COMPLETED},
        CallState.ANSWERED: {CallState.CONNECTED, CallState.COMPLETED, CallState.FAILED},
        CallState.CONNECTED: {CallState.COMPLETED, CallState.FAILED},
        CallState.COMPLETED: set(),
        CallState.FAILED: set(),
        CallState.CANCELLED: set()
    }

    @classmethod
    def transition(cls, call: Call, target_state: CallState) -> bool:
        # 1. Strictly block any modification once terminal state is reached
        if call.state in TERMINAL_CALL_STATES:
            return False

        # 2. Block backward or identical state transitions
        if target_state.value <= call.state.value and target_state not in TERMINAL_CALL_STATES:
            return False

        # 3. Verify valid transition path
        if target_state in cls.VALID_TRANSITIONS.get(call.state, set()):
            call.state = target_state
            call.state_seq += 1
            return True

        return False
