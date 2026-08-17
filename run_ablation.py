"""Reproducible A-BA-QEC component ablation study."""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from a_ba_qec import ABBQECDecoder
from run_benchmark import generate_scenario, run_method


def run_variant(name, enabled, scenarios, shots=400, n_qubits=16, seed=20260817):
    rows = []
    for index, scenario in enumerate(scenarios):
        data = generate_scenario(scenario, n_qubits, shots, seed + index)
        decoder = ABBQECDecoder(n_qubits, seed=seed + index, enabled=enabled)
        failures = 0
        latencies = []
        complexities = []
        for target, observed, labels, _ in data:
            result = decoder.decode(observed, target=target, error_labels=labels)
            failures += int(not result.success)
            latencies.append(result.latency_seconds)
            complexities.append(result.candidate_count * n_qubits)
        rows.append({
            "variant": name, "scenario": scenario, "seed": seed + index,
            "physical_error_rate": sum(item[3] for item in data) / len(data),
            "logical_error_rate": failures / len(data),
            "decoding_latency_ms": 1000 * sum(latencies) / len(latencies),
            "computational_complexity": sum(complexities) / len(complexities),
            "memory_usage_records": decoder.memory.snapshot()["short_term"] + decoder.memory.snapshot()["long_term"],
            "adaptation_speed": next((i for i in range(len(data)) if decoder.genome.last_change and decoder.genome.last_change.new_regime > 0), len(data)),
        })
    return rows


def main():
    scenarios = ["depolarizing", "asymmetric", "temporal_correlation", "burst_errors", "progressive_drift", "abrupt_regime_change", "hardware_inspired"]
    variants = {
        "A-BA-QEC": {},
        "A-BA-QEC - Noise Genome": {"noise_genome": False},
        "A-BA-QEC - Immune Memory": {"immune_memory": False},
        "A-BA-QEC - Mutation": {"mutation": False},
        "A-BA-QEC - Homeostasis": {"homeostasis": False},
        "A-BA-QEC - Attention": {"attention": False},
    }
    rows = []
    for name, disabled in variants.items():
        enabled = {key: True for key in ["noise_genome", "immune_memory", "mutation", "homeostasis", "attention"]}
        enabled.update(disabled)
        rows.extend(run_variant(name, enabled, scenarios))
    (ROOT / "results" / "ablation_results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with (ROOT / "results" / "ablation_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(f"Saved {len(rows)} ablation rows")


if __name__ == "__main__":
    main()
