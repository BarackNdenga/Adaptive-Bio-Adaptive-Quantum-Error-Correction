"""Generate reproducible benchmark and ablation figures."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "results" / name).read_text(encoding="utf-8"))


def benchmark_figures():
    rows = load("benchmark_results.json")
    scenarios = list(dict.fromkeys(row["scenario"] for row in rows))
    methods = ["MWPM", "BA-QEC", "A-BA-QEC"]
    metrics = [("logical_error_rate", "Logical error rate", "logical_error_rate.png"), ("decoding_latency_ms", "Decoding latency (ms)", "latency.png"), ("computational_complexity", "Computational complexity proxy", "complexity.png"), ("robustness_under_drift", "Robustness under drift", "robustness.png")]
    for key, ylabel, filename in metrics:
        fig, ax = plt.subplots(figsize=(13, 6))
        x = np.arange(len(scenarios))
        width = 0.25
        for index, method in enumerate(methods):
            values = [next(row[key] for row in rows if row["scenario"] == scenario and row["method"] == method) for scenario in scenarios]
            ax.bar(x + (index - 1) * width, values, width, label=method)
        ax.set_xticks(x, scenarios, rotation=25, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_title(f"MWPM vs BA-QEC vs A-BA-QEC — {ylabel}")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(ROOT / "figures" / filename, dpi=160)
        plt.close(fig)


def ablation_figure():
    rows = load("ablation_results.json")
    variants = list(dict.fromkeys(row["variant"] for row in rows))
    scenarios = list(dict.fromkeys(row["scenario"] for row in rows))
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(scenarios))
    width = 0.13
    for index, variant in enumerate(variants):
        values = [next(row["logical_error_rate"] for row in rows if row["scenario"] == scenario and row["variant"] == variant) for scenario in scenarios]
        ax.bar(x + (index - len(variants) / 2) * width, values, width, label=variant)
    ax.set_xticks(x, scenarios, rotation=25, ha="right")
    ax.set_ylabel("Logical error rate")
    ax.set_title("A-BA-QEC mandatory ablation study")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "ablation_logical_error_rate.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    benchmark_figures()
    ablation_figure()
    print("Figures written to figures/")
