"""Continuous adaptive decoding loop for A-BA-QEC."""
from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, Optional, Sequence

import numpy as np

from .adaptive_response import AdaptiveWeightPolicy, SyndromeAttentionEngine
from .clonal_evolution import CandidateStrategy, ClonalEvolutionEngine
from .homeostasis import ImmuneHomeostasis
from .immune_memory import ArtificialImmuneMemory
from .noise_genome import NoiseGenomeEngine


@dataclass
class DecodeResult:
    correction: np.ndarray
    success: bool
    latency_seconds: float
    regime_id: int
    activity_level: str
    candidate_count: int
    attention_score: float
    diagnostics: Dict[str, float] = field(default_factory=dict)


class ABBQECDecoder:
    """A deterministic, model-agnostic adaptive decoder for controlled studies."""

    def __init__(self, n_qubits: int, seed: int = 0, enabled: Optional[Dict[str, bool]] = None) -> None:
        self.n_qubits = n_qubits
        self.rng = np.random.default_rng(seed)
        self.enabled = {
            "noise_genome": True, "immune_memory": True, "mutation": True,
            "homeostasis": True, "attention": True,
        }
        if enabled:
            self.enabled.update(enabled)
        self.genome = NoiseGenomeEngine(n_qubits=n_qubits)
        self.memory = ArtificialImmuneMemory()
        self.clones = ClonalEvolutionEngine(seed=seed)
        self.homeostasis = ImmuneHomeostasis()
        self.attention = SyndromeAttentionEngine()
        self.weights = AdaptiveWeightPolicy(n_qubits)
        self.error_rate_ema = 0.0
        self.last_strategy = np.zeros(n_qubits, dtype=int)
        self.steps = 0

    def decode(
        self,
        syndrome: Sequence[int],
        target: Optional[Sequence[int]] = None,
        error_labels: Optional[Sequence[str]] = None,
    ) -> DecodeResult:
        started = perf_counter()
        syndrome_array = np.asarray(syndrome, dtype=int).reshape(-1)
        if syndrome_array.size != self.n_qubits:
            raise ValueError("syndrome length does not match n_qubits")
        genome = self.genome.observe(syndrome_array, error_labels=error_labels) if self.enabled["noise_genome"] else self.genome.signature
        if genome is None:
            genome = self.genome.observe(syndrome_array)
        memory_best = self.memory.best(syndrome_array) if self.enabled["immune_memory"] else None
        confidence = memory_best.confidence if memory_best else 0.25
        instability = min(1.0, genome.drift + (0.5 if genome.regime_id > 0 else 0.0))
        state = self.homeostasis.decide(self.error_rate_ema, genome.drift, instability, confidence) if self.enabled["homeostasis"] else self.homeostasis.state
        affinity = memory_best.score() if memory_best else 0.25
        attention_score = self.attention.score(syndrome_array, affinity, confidence, genome) if self.enabled["attention"] else None
        if memory_best is not None:
            parent = np.asarray(memory_best.strategy, dtype=int)
        else:
            parent = syndrome_array.copy()
        candidates = [
            CandidateStrategy(parent, affinity, parent.copy(), 0.0, self.steps),
            CandidateStrategy(np.zeros(self.n_qubits, dtype=int), 0.35, parent.copy(), 0.0, self.steps),
        ]
        if self.enabled["mutation"]:
            candidates.extend(self.clones.evolve(parent, 1.0 if memory_best and memory_best.confidence >= 0.6 else 0.0, state.candidate_budget, instability))

        # Selection uses only the syndrome, learned affinity and sparsity prior.
        # ``target`` is reserved strictly for post-hoc evaluation.
        def score(candidate: CandidateStrategy) -> float:
            distance = float(np.mean(candidate.strategy != syndrome_array))
            sparsity_penalty = 0.10 * float(np.mean(candidate.strategy))
            return distance - 0.10 * candidate.affinity + sparsity_penalty

        selected = min(candidates, key=score)
        target_array = None if target is None else np.asarray(target, dtype=int).reshape(-1)
        if target_array is not None and target_array.size != self.n_qubits:
            raise ValueError("target length does not match n_qubits")
        success = target_array is not None and np.array_equal(selected.strategy, target_array)
        reward = 1.0 if success else (0.25 if target is None else 0.0)
        if self.enabled["immune_memory"]:
            self.memory.update(syndrome_array, selected.strategy, reward, genome.regime_id, instability, selected.affinity)
        if error_labels is not None:
            for qubit, label in enumerate(error_labels):
                self.weights.observe(qubit, label, genome.temporal_correlation > 0.5)
        self.error_rate_ema = 0.95 * self.error_rate_ema + 0.05 * (0.0 if success else 1.0)
        self.last_strategy = selected.strategy.copy()
        self.steps += 1
        return DecodeResult(
            correction=selected.strategy.copy(), success=bool(success), latency_seconds=perf_counter() - started,
            regime_id=genome.regime_id, activity_level=state.level, candidate_count=len(candidates),
            attention_score=attention_score.score if attention_score else 0.0,
            diagnostics={"noise_drift": genome.drift, "confidence": confidence, "affinity": selected.affinity},
        )
