"""Adaptive computational activity control for A-BA-QEC."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HomeostaticState:
    level: str
    activity: float
    candidate_budget: int
    exploration: float
    reason: str


class ImmuneHomeostasis:
    def __init__(self, low_budget: int = 2, normal_budget: int = 5, high_budget: int = 10, emergency_budget: int = 20) -> None:
        self.budgets = {"low": low_budget, "normal": normal_budget, "high": high_budget, "emergency": emergency_budget}
        if any(value < 1 for value in self.budgets.values()):
            raise ValueError("activity budgets must be positive")
        self.state = HomeostaticState("normal", 0.5, normal_budget, 0.25, "initial")

    def decide(self, error_rate: float, drift: float, instability: float, confidence: float) -> HomeostaticState:
        error_rate = float(np.clip(error_rate, 0.0, 1.0))
        drift = float(np.clip(drift, 0.0, 1.0))
        instability = float(np.clip(instability, 0.0, 1.0))
        confidence = float(np.clip(confidence, 0.0, 1.0))
        activity = float(np.clip(0.35 * error_rate + 0.30 * drift + 0.25 * instability + 0.10 * (1.0 - confidence), 0.0, 1.0))
        if error_rate >= 0.35 or drift >= 0.45:
            level, reason = "emergency", "severe noise or drift"
        elif instability >= 0.25 or confidence <= 0.40:
            level, reason = "high", "unstable regime or low confidence"
        elif error_rate <= 0.05 and drift <= 0.05 and confidence >= 0.75:
            level, reason = "low", "stable low-noise regime"
        else:
            level, reason = "normal", "intermediate conditions"
        exploration = {"low": 0.05, "normal": 0.20, "high": 0.55, "emergency": 0.90}[level]
        self.state = HomeostaticState(level, activity, self.budgets[level], exploration, reason)
        return self.state
