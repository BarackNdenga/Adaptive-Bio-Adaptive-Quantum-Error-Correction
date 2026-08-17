"""Adaptive graph-weight response and syndrome attention for A-BA-QEC."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

from .noise_genome import NoiseGenomeSignature


@dataclass(frozen=True)
class AttentionScore:
    syndrome_key: Tuple[int, ...]
    score: float
    affinity: float
    recurrence: float
    confidence: float
    spatial_correlation: float
    temporal_correlation: float
    drift: float


class SyndromeAttentionEngine:
    def __init__(self, weights: Optional[Sequence[float]] = None) -> None:
        self.weights = np.asarray(weights if weights is not None else [0.25] * 6, dtype=float)
        if self.weights.size != 6 or np.any(self.weights < 0) or self.weights.sum() == 0:
            raise ValueError("attention weights must contain six non-negative values")
        self.weights /= self.weights.sum()
        self.recurrence: Dict[Tuple[int, ...], int] = {}

    def score(self, syndrome: Sequence[int], affinity: float, confidence: float, genome: NoiseGenomeSignature) -> AttentionScore:
        key = tuple(int(x) for x in syndrome)
        self.recurrence[key] = self.recurrence.get(key, 0) + 1
        recurrence = float(1.0 - np.exp(-self.recurrence[key] / 5.0))
        values = np.asarray([affinity, recurrence, confidence, genome.spatial_correlation, genome.temporal_correlation, genome.drift], dtype=float)
        values = np.clip(values, 0.0, 1.0)
        return AttentionScore(key, float(np.dot(self.weights, values)), *values.tolist())

    def rank(self, items: Iterable[AttentionScore]) -> list[AttentionScore]:
        return sorted(items, key=lambda item: item.score, reverse=True)


class AdaptiveWeightPolicy:
    """Translate a noise genome into per-qubit error-type graph multipliers."""

    def __init__(self, n_qubits: int, prior: float = 1.0, learning_rate: float = 0.20) -> None:
        if n_qubits < 1 or prior <= 0 or not 0 < learning_rate <= 1:
            raise ValueError("invalid adaptive weight policy parameters")
        self.n_qubits = n_qubits
        self.learning_rate = learning_rate
        self.error_counts = np.full((n_qubits, 3), prior, dtype=float)
        self.temporal_counts = np.full(n_qubits, prior, dtype=float)

    def observe(self, qubit: int, error_type: str, temporally_correlated: bool = False) -> None:
        if not 0 <= qubit < self.n_qubits or error_type.upper() not in {"X", "Y", "Z"}:
            raise ValueError("invalid qubit or error type")
        axis = {"X": 0, "Y": 1, "Z": 2}[error_type.upper()]
        self.error_counts[qubit, axis] += 1.0
        if temporally_correlated:
            self.temporal_counts[qubit] += 1.0

    def probabilities(self) -> np.ndarray:
        return self.error_counts / self.error_counts.sum(axis=1, keepdims=True)

    def multipliers(self, genome: NoiseGenomeSignature) -> np.ndarray:
        probs = self.probabilities()
        global_profile = np.asarray([genome.px, genome.py, genome.pz], dtype=float)
        global_profile = global_profile / max(global_profile.sum(), 1e-12)
        blended = 0.7 * probs + 0.3 * global_profile
        temporal = self.temporal_counts / self.temporal_counts.max()
        return np.concatenate([blended, temporal[:, None]], axis=1)

    def effective_edge_weight(self, base_weight: float, qubit: int, error_type: str, genome: NoiseGenomeSignature) -> float:
        multipliers = self.multipliers(genome)
        axis = {"X": 0, "Y": 1, "Z": 2}[error_type.upper()]
        likelihood = float(np.clip(multipliers[qubit, axis], 1e-6, 1.0))
        return float(base_weight / likelihood)
