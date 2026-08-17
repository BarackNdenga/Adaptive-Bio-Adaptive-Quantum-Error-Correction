"""Clonal expansion and mutation engine for A-BA-QEC."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np


@dataclass
class CandidateStrategy:
    strategy: np.ndarray
    affinity: float
    parent: np.ndarray
    mutation_rate: float
    generation: int


class ClonalEvolutionEngine:
    def __init__(self, seed: int = 0, expansion_factor: int = 4, mutation_rate: float = 0.15) -> None:
        if expansion_factor < 1 or not 0.0 <= mutation_rate <= 1.0:
            raise ValueError("invalid clonal evolution parameters")
        self.rng = np.random.default_rng(seed)
        self.expansion_factor = expansion_factor
        self.mutation_rate = mutation_rate
        self.generation = 0

    def evolve(
        self,
        parent: Sequence[int],
        reward: float,
        budget: int,
        regime_instability: float = 0.0,
    ) -> List[CandidateStrategy]:
        parent_array = np.asarray(parent, dtype=int).reshape(-1)
        if parent_array.size == 0 or np.any((parent_array != 0) & (parent_array != 1)):
            raise ValueError("strategy must be a non-empty binary vector")
        budget = max(1, int(budget))
        instability = float(np.clip(regime_instability, 0.0, 1.0))
        rate = float(np.clip(self.mutation_rate * (1.0 + instability), 0.0, 1.0))
        self.generation += 1
        candidates: List[CandidateStrategy] = []
        for index in range(min(budget, self.expansion_factor if reward >= 0.5 else budget)):
            if reward >= 0.5 and index == 0:
                child = parent_array.copy()
                child_rate = 0.0
            else:
                child = parent_array.copy()
                mask = self.rng.random(child.size) < rate
                child[mask] ^= 1
                child_rate = rate
            affinity = self._affinity(child, parent_array, reward, instability)
            candidates.append(CandidateStrategy(child, affinity, parent_array.copy(), child_rate, self.generation))
        return sorted(candidates, key=lambda candidate: candidate.affinity, reverse=True)

    @staticmethod
    def _affinity(child: np.ndarray, parent: np.ndarray, reward: float, instability: float) -> float:
        similarity = 1.0 - float(np.mean(child != parent))
        exploration_bonus = instability * float(np.mean(child != parent))
        return float(np.clip(0.60 * reward + 0.30 * similarity + 0.10 * exploration_bonus, 0.0, 1.0))
