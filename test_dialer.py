import unittest
import threading
from core.state_machines import Agent, AgentState, Call, CallState, CallStateMachine
from core.call_allocator import CallAllocator
from core.safety_controller import SafetyController

class TestSmartDialer(unittest.TestCase):
    def test_concurrent_agent_reservation(self):
        """Validates that 2 workers seeing 1 agent cannot double-reserve."""
        allocator = CallAllocator()
        agents = [Agent(agent_id="agent_1", state=AgentState.AVAILABLE)]
        results = []

        def worker_task():
            res = allocator.reserve_agent_atomic(agents)
            if res:
                results.append(res.agent_id)

        t1 = threading.Thread(target=worker_task)
        t2 = threading.Thread(target=worker_task)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(len(results), 1)
        self.assertEqual(agents[0].state, AgentState.RESERVED)

    def test_out_of_order_and_duplicate_events(self):
        """Verifies state machine idempotency and monotonic progression."""
        call = Call(call_id="c1", borrower_id="b1")
        
        # Valid progression: QUEUED -> RESERVED -> INITIATED -> RINGING -> COMPLETED
        self.assertTrue(CallStateMachine.transition(call, CallState.RESERVED))
        self.assertTrue(CallStateMachine.transition(call, CallState.INITIATED))
        self.assertTrue(CallStateMachine.transition(call, CallState.RINGING))
        self.assertTrue(CallStateMachine.transition(call, CallState.COMPLETED))
        
        # Duplicate / out-of-order events after COMPLETED must be strictly rejected
        self.assertFalse(CallStateMachine.transition(call, CallState.INITIATED))
        self.assertFalse(CallStateMachine.transition(call, CallState.RINGING))
        self.assertEqual(call.state, CallState.COMPLETED)

    def test_safety_controller_overdial_cap(self):
        """Ensures safety controller caps explosive predictive pacing."""
        controller = SafetyController()
        context = {
            "available_agents": 2,
            "expected_free_agents": 1,
            "ringing_calls": 3,
            "mode": "PREDICTIVE",
            "provider_health": 1.0
        }
        # Total capacity = 3. 3 * 1.5 = 4 allowed in flight. With 3 ringing, max allowed dials = 1.
        approved = controller.evaluate(proposed_dials=10, context=context)
        self.assertEqual(approved, 1)

if __name__ == "__main__":
    unittest.main()
