import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from a_ba_qec import AdaptiveMWPM, AdaptiveWeightPolicy, NoiseGenomeSignature


def test_adaptive_mwpm_weight_profile():
    genome = NoiseGenomeSignature(0.6, 0.2, 0.1, 0.1, 0.4, 0.0, 5, 0)
    policy = AdaptiveWeightPolicy(2)
    for _ in range(8):
        policy.observe(0, 'X')
    adapter = AdaptiveMWPM(edge_qubits=[0, 0], edge_types=['X', 'Z'])
    weights = adapter.adapt_weights(genome, policy)
    assert weights[0] < weights[1]
