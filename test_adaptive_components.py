import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from a_ba_qec import (
    AdaptiveWeightPolicy,
    ClonalEvolutionEngine,
    ImmuneHomeostasis,
    NoiseGenomeSignature,
    SyndromeAttentionEngine,
)


def test_clonal_engine_expands_and_mutates():
    engine = ClonalEvolutionEngine(seed=7, expansion_factor=4, mutation_rate=1.0)
    candidates = engine.evolve([0, 0, 0], reward=0.0, budget=4, regime_instability=1.0)
    assert len(candidates) == 4
    assert any(not np.array_equal(item.strategy, [0, 0, 0]) for item in candidates)
    assert all(0.0 <= item.affinity <= 1.0 for item in candidates)


def test_homeostasis_changes_budget():
    controller = ImmuneHomeostasis()
    low = controller.decide(0.01, 0.01, 0.01, 0.95)
    emergency = controller.decide(0.6, 0.8, 0.8, 0.1)
    assert low.level == 'low'
    assert emergency.level == 'emergency'
    assert emergency.candidate_budget > low.candidate_budget


def test_attention_tracks_recurrence():
    genome = NoiseGenomeSignature(0.2, 0.1, 0.05, 0.3, 0.4, 0.1, 3, 0)
    attention = SyndromeAttentionEngine()
    first = attention.score([1, 0], 0.4, 0.5, genome)
    second = attention.score([1, 0], 0.4, 0.5, genome)
    assert second.recurrence > first.recurrence
    assert second.score > first.score


def test_adaptive_policy_learns_qubit_error_type():
    genome = NoiseGenomeSignature(0.5, 0.2, 0.1, 0.2, 0.3, 0.0, 5, 0)
    policy = AdaptiveWeightPolicy(3)
    for _ in range(10):
        policy.observe(0, 'X')
        policy.observe(1, 'Z')
    probs = policy.probabilities()
    assert probs[0, 0] > probs[0, 2]
    assert probs[1, 2] > probs[1, 0]
    assert policy.effective_edge_weight(1.0, 0, 'X', genome) < policy.effective_edge_weight(1.0, 0, 'Z', genome)
