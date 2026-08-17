"""Optional PyMatching integration for adaptive A-BA-QEC weights."""
from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np

from .adaptive_response import AdaptiveWeightPolicy
from .noise_genome import NoiseGenomeSignature


class AdaptiveMWPM:
    """Keep the original MWPM path intact while exposing adaptive weights.

    ``edge_qubits`` and ``edge_types`` are optional because detector-error
    models do not universally expose a stable physical-qubit annotation. When
    omitted, a deterministic global profile is used and the selected weights
    remain inspectable for benchmarking.
    """

    def __init__(self, model=None, edge_qubits: Optional[Sequence[int]] = None, edge_types: Optional[Sequence[str]] = None):
        self.model = model
        self.edge_qubits = list(edge_qubits) if edge_qubits is not None else None
        self.edge_types = list(edge_types) if edge_types is not None else None
        self.matcher = None
        if model is not None:
            try:
                import pymatching
                self.matcher = pymatching.Matching.from_detector_error_model(model)
            except ImportError:
                self.matcher = None

    def adapt_weights(self, genome: NoiseGenomeSignature, policy: AdaptiveWeightPolicy) -> np.ndarray:
        if self.edge_qubits is not None and self.edge_types is not None:
            weights = np.asarray([
                policy.effective_edge_weight(1.0, qubit, error_type, genome)
                for qubit, error_type in zip(self.edge_qubits, self.edge_types)
            ], dtype=float)
        else:
            profile = np.asarray([genome.px, genome.py, genome.pz], dtype=float)
            profile /= max(profile.sum(), 1e-12)
            weights = 1.0 / np.clip(profile, 1e-6, 1.0)
        if self.matcher is not None and self.edge_qubits is not None:
            for index, weight in enumerate(weights[: self.matcher.num_edges]):
                self.matcher.set_weight(index, float(weight))
        return weights

    def decode(self, syndrome: Sequence[int]) -> np.ndarray:
        if self.matcher is None:
            raise RuntimeError("PyMatching matcher is unavailable; use an installed pymatching dependency")
        return np.asarray(self.matcher.decode(np.asarray(syndrome, dtype=np.uint8)))
