"""Dynamic noise-genome estimation for the A-BA-QEC experimental stack."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class NoiseGenomeSignature:
    """A compact, serialisable representation of the observed noise regime."""

    px: float
    py: float
    pz: float
    spatial_correlation: float
    temporal_correlation: float
    drift: float
    sample_count: int
    regime_id: int

    def as_vector(self) -> np.ndarray:
        return np.asarray(
            [self.px, self.py, self.pz, self.spatial_correlation,
             self.temporal_correlation, self.drift], dtype=float
        )

    @property
    def dominant_error(self) -> str:
        return ("X", "Y", "Z")[int(np.argmax([self.px, self.py, self.pz]))]


@dataclass(frozen=True)
class RegimeChange:
    previous_regime: int
    new_regime: int
    distance: float
    signature: NoiseGenomeSignature


class NoiseGenomeEngine:
    """Estimate a dynamic noise signature from sequential syndrome observations.

    ``error_labels`` may contain ``X``, ``Y`` and ``Z`` labels per qubit. When
    labels are unavailable, binary syndrome vectors are still used to estimate
    spatial/temporal structure and total activity. ``qubit_ids`` makes the
    profile usable by an adaptive graph-weight policy.
    """

    def __init__(
        self,
        n_qubits: Optional[int] = None,
        window_size: int = 32,
        baseline_size: int = 8,
        change_threshold: float = 0.20,
        smoothing: float = 0.20,
    ) -> None:
        if window_size < 2 or baseline_size < 1:
            raise ValueError("window_size must be >= 2 and baseline_size must be >= 1")
        if not 0.0 < smoothing <= 1.0:
            raise ValueError("smoothing must be in (0, 1]")
        self.n_qubits = n_qubits
        self.window_size = window_size
        self.baseline_size = baseline_size
        self.change_threshold = change_threshold
        self.smoothing = smoothing
        self._observations: Deque[np.ndarray] = deque(maxlen=window_size)
        self._labels: Deque[Optional[Tuple[str, ...]]] = deque(maxlen=window_size)
        self._previous_vector: Optional[np.ndarray] = None
        self._reference_vector: Optional[np.ndarray] = None
        self._signature: Optional[NoiseGenomeSignature] = None
        self._regime_id = 0
        self._updates = 0
        self._last_change: Optional[RegimeChange] = None

    @property
    def signature(self) -> Optional[NoiseGenomeSignature]:
        return self._signature

    @property
    def last_change(self) -> Optional[RegimeChange]:
        return self._last_change

    def observe(
        self,
        syndrome: Sequence[float],
        error_labels: Optional[Sequence[str]] = None,
    ) -> NoiseGenomeSignature:
        vector = np.asarray(syndrome, dtype=float).reshape(-1)
        if vector.size == 0:
            raise ValueError("syndrome cannot be empty")
        if np.any((vector < 0) | (vector > 1)):
            raise ValueError("syndrome values must be in [0, 1]")
        if self.n_qubits is None:
            self.n_qubits = int(vector.size)
        if vector.size != self.n_qubits:
            raise ValueError("syndrome length does not match n_qubits")

        labels: Optional[Tuple[str, ...]] = None
        if error_labels is not None:
            labels = tuple(str(label).upper() for label in error_labels)
            if len(labels) != vector.size or any(label not in {"X", "Y", "Z"} for label in labels):
                raise ValueError("error_labels must have one of X, Y or Z per qubit")
        self._observations.append(vector.copy())
        self._labels.append(labels)
        raw = self._estimate_raw_signature()
        smoothed = raw if self._previous_vector is None else (
            (1.0 - self.smoothing) * self._previous_vector + self.smoothing * raw
        )
        drift = 0.0 if self._reference_vector is None else self._distance(smoothed, self._reference_vector[:5])
        current = np.concatenate([smoothed[:5], [drift]])
        previous = self._regime_id
        initializing = self._reference_vector is None
        change_distance = 0.0 if initializing else self._distance(current, self._reference_vector)
        changed = (not initializing) and change_distance >= self.change_threshold
        if changed:
            self._regime_id += 1
            self._reference_vector = current.copy()
        elif initializing and self._updates + 1 >= self.baseline_size:
            self._reference_vector = current.copy()
        self._previous_vector = smoothed.copy()
        self._updates += 1
        self._signature = NoiseGenomeSignature(
            px=float(smoothed[0]), py=float(smoothed[1]), pz=float(smoothed[2]),
            spatial_correlation=float(smoothed[3]), temporal_correlation=float(smoothed[4]),
            drift=float(drift), sample_count=len(self._observations), regime_id=self._regime_id,
        )
        if changed:
            self._last_change = RegimeChange(previous, self._regime_id, change_distance, self._signature)
        return self._signature

    def _estimate_raw_signature(self) -> np.ndarray:
        observations = np.vstack(self._observations)
        labels = [label for label in self._labels if label is not None]
        if labels:
            flat = np.asarray([item for row in labels for item in row])
            probs = np.asarray([(flat == axis).mean() for axis in ("X", "Y", "Z")])
        else:
            activity = observations.mean()
            probs = np.asarray([activity / 3.0] * 3)
        spatial = self._spatial_correlation(observations)
        temporal = self._temporal_correlation(observations)
        return np.asarray([*probs, spatial, temporal], dtype=float)

    @staticmethod
    def _spatial_correlation(observations: np.ndarray) -> float:
        if observations.shape[1] < 2 or observations.shape[0] < 2:
            return 0.0
        left, right = observations[:, :-1], observations[:, 1:]
        return float(np.mean((left == right) & (left > 0)))

    @staticmethod
    def _temporal_correlation(observations: np.ndarray) -> float:
        if observations.shape[0] < 2:
            return 0.0
        return float(np.mean(observations[1:] == observations[:-1]))

    @staticmethod
    def _distance(first: np.ndarray, second: np.ndarray) -> float:
        return float(np.mean(np.abs(first - second)))
