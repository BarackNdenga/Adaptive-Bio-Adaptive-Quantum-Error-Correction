import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from decoder import simulate_baqec_demo


def test_original_baqec_still_runs_and_is_deterministic():
    first = simulate_baqec_demo(n_shots=500, seed=123)
    second = simulate_baqec_demo(n_shots=500, seed=123)
    assert first == second
    assert len(first) == 2
    assert all(0.0 <= value <= 1.0 for value in first)
