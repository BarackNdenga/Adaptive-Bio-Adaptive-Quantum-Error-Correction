"""Artificial immune memory for adaptive QEC strategies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class MemoryRecord:
    syndrome_key: Tuple[int, ...]
    strategy: Tuple[int, ...]
    confidence: float = 0.5
    support: float = 0.0
    trials: int = 0
    successes: int = 0
    last_reward: float = 0.0
    age: int = 0
    regime_id: int = 0

    @property
    def empirical_success(self) -> float:
        return self.successes / self.trials if self.trials else 0.0

    def score(self) -> float:
        return float(0.65 * self.confidence + 0.25 * self.empirical_success + 0.10 * self.support)


class ArtificialImmuneMemory:
    """Two-tier strategy memory with reinforcement and controlled forgetting.

    The confidence update follows ``M(t)=lambda*M(t-1)+(1-lambda)*R(t)``.
    Rewards are expected in ``[0, 1]``. A lower lambda is used during unstable
    regimes so stale strategies are forgotten faster.
    """

    def __init__(
        self,
        short_term_capacity: int = 128,
        long_term_capacity: int = 512,
        lambda_base: float = 0.90,
        forget_after: int = 20,
        prune_threshold: float = 0.08,
    ) -> None:
        if short_term_capacity < 1 or long_term_capacity < 1:
            raise ValueError("memory capacities must be positive")
        if not 0.0 <= lambda_base < 1.0:
            raise ValueError("lambda_base must be in [0, 1)")
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.lambda_base = lambda_base
        self.forget_after = forget_after
        self.prune_threshold = prune_threshold
        self.short_term: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], MemoryRecord] = {}
        self.long_term: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], MemoryRecord] = {}
        self.step = 0

    @staticmethod
    def _key(syndrome: Sequence[int], strategy: Sequence[int]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        return tuple(int(x) for x in syndrome), tuple(int(x) for x in strategy)

    @staticmethod
    def _regime_lambda(base: float, regime_instability: float) -> float:
        instability = float(np.clip(regime_instability, 0.0, 1.0))
        return float(np.clip(base - 0.45 * instability, 0.05, 0.995))

    def update(
        self,
        syndrome: Sequence[int],
        strategy: Sequence[int],
        reward: float,
        regime_id: int = 0,
        regime_instability: float = 0.0,
        support: float = 0.0,
    ) -> MemoryRecord:
        reward = float(np.clip(reward, 0.0, 1.0))
        self._age_records()
        key = self._key(syndrome, strategy)
        record = self.short_term.get(key) or self.long_term.get(key)
        if record is None:
            record = MemoryRecord(key[0], key[1], regime_id=regime_id)
        lam = self._regime_lambda(self.lambda_base, regime_instability)
        record.confidence = lam * record.confidence + (1.0 - lam) * reward
        record.support = float(np.clip(0.90 * record.support + 0.10 * support, 0.0, 1.0))
        record.trials += 1
        record.successes += int(reward >= 0.5)
        record.last_reward = reward
        record.age = 0
        record.regime_id = regime_id
        self.step += 1
        self.short_term[key] = record
        if reward >= 0.75 or record.confidence >= 0.72:
            self.long_term[key] = record
        self._decay_and_prune()
        self._rebalance()
        return MemoryRecord(**vars(record))

    def _age_records(self) -> None:
        seen = set()
        for store in (self.short_term, self.long_term):
            for record in store.values():
                if id(record) not in seen:
                    record.age += 1
                    seen.add(id(record))

    def _decay_and_prune(self) -> None:
        for store in (self.short_term, self.long_term):
            remove = []
            for key, record in store.items():
                if record.age > 0:
                    record.confidence *= 0.98
                if record.age >= self.forget_after and (
                    record.confidence < self.prune_threshold or record.empirical_success < 0.5
                ):
                    remove.append(key)
            for key in remove:
                store.pop(key, None)

    def _rebalance(self) -> None:
        if len(self.short_term) > self.short_term_capacity:
            ranked = sorted(self.short_term, key=lambda k: self.short_term[k].score(), reverse=True)
            self.short_term = {k: self.short_term[k] for k in ranked[: self.short_term_capacity]}
        if len(self.long_term) > self.long_term_capacity:
            ranked = sorted(self.long_term, key=lambda k: self.long_term[k].score(), reverse=True)
            self.long_term = {k: self.long_term[k] for k in ranked[: self.long_term_capacity]}

    def recall(self, syndrome: Sequence[int], limit: int = 8) -> List[MemoryRecord]:
        key = tuple(int(x) for x in syndrome)
        records = [r for r in list(self.short_term.values()) + list(self.long_term.values()) if r.syndrome_key == key]
        unique = {self._key(r.syndrome_key, r.strategy): r for r in records}
        return sorted(unique.values(), key=lambda r: r.score(), reverse=True)[:limit]

    def best(self, syndrome: Sequence[int]) -> Optional[MemoryRecord]:
        records = self.recall(syndrome, limit=1)
        return records[0] if records else None

    def tick(self) -> None:
        """Advance age without an observation, enabling gradual forgetting."""
        self.step += 1
        self._age_records()
        self._decay_and_prune()

    def snapshot(self) -> Dict[str, int]:
        return {"short_term": len(self.short_term), "long_term": len(self.long_term), "step": self.step}
