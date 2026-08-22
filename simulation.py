from core.data_loader import DatasetLoader
from engine import SmartDialer
from core.mock_providers import ProviderA, ProviderB

def run_real_dataset_simulation():
    loader = DatasetLoader()
    agent_ids = loader.load_agents()
    borrower_queue = loader.load_target_borrowers()
    historical_ans_rate, historical_att = loader.compute_historical_pacing_stats()

    print("=" * 65)
    print("      SMART DIALER: REAL DATASET BENCHMARK SIMULATION")
    print("=" * 65)
    print(f"Total Agents Ingested:        {len(agent_ids)}")
    print(f"Total Target Borrowers:       {len(borrower_queue)}")
    print(f"Historical Answer Rate:       {int(historical_ans_rate * 100)}%")
    print(f"Average Talk Time (ATT):      {historical_att}s\n")

    dialer = SmartDialer(mode="PREDICTIVE")
    dialer.borrower_queue = borrower_queue
    for a_id in agent_ids[:50]:  # Seed pool with first 50 agents
        dialer.register_agent(a_id)

    print(f"{'Cycle':<7} | {'Pacing Dials':<13} | {'Safety Approved':<16} | {'Initiated':<10} | {'Connected':<10} | {'Abandoned':<10}")
    print("-" * 75)

    for cycle in range(1, 11):
        dialer.run_cycle(answer_rate=historical_ans_rate, avg_talk_time=historical_att)
        m = dialer.metrics
        print(f"#{cycle:<6} | {m['pacing_requested']:<13} | {m['safety_approved']:<16} | {m['calls_initiated']:<10} | {m['calls_connected']:<10} | {m['abandoned_calls']:<10}")

    print("\n" + "=" * 65)
    print("                    BENCHMARK COMPLETED")
    print("=" * 65)

if __name__ == "__main__":
    run_real_dataset_simulation()