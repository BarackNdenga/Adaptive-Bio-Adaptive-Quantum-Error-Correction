import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from a_ba_qec.immune_memory import ArtificialImmuneMemory


def test_reinforcement_and_recall():
    memory = ArtificialImmuneMemory(lambda_base=0.5)
    for _ in range(5):
        record = memory.update([1, 0], [0, 1], reward=1.0, support=1.0)
    assert record.confidence > 0.9
    assert memory.best([1, 0]).strategy == (0, 1)


def test_adaptive_lambda_reacts_to_instability():
    memory = ArtificialImmuneMemory(lambda_base=0.9)
    stable = memory.update([1], [0], reward=1.0, regime_instability=0.0)
    unstable = memory.update([1], [0], reward=0.0, regime_instability=1.0)
    assert unstable.confidence < stable.confidence


def test_forgetting_removes_stale_records():
    memory = ArtificialImmuneMemory(forget_after=2, prune_threshold=0.2, lambda_base=0.5)
    memory.update([1], [0], reward=0.0)
    memory.tick()
    memory.tick()
    memory.tick()
    assert memory.best([1]) is None
