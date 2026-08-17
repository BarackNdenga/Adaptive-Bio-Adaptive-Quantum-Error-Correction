"""
simulations/hamming_cdr3.py

Quick-and-dirty TCR CDR3 "distance statistics" script.

This script either:
- loads CDR3 amino-acid sequences from `data/sample_cdr3.csv` if it exists, or
- generates a small synthetic dataset and saves it there.

It then computes simple Hamming distance statistics between sequences
(same-length pairs only) and prints summary numbers.

The goal is not biological accuracy, but to provide a concrete script that
demonstrates how TCR-like diversity yields high code distances.
"""

import csv
import random
from pathlib import Path
from typing import List

import numpy as np

DATA_PATH = Path("data") / "sample_cdr3.csv"

AMINO_ALPHABET = "ACDEFGHIKLMNPQRSTVWY"  # 20 standard amino acids


def generate_synthetic_cdr3(n: int = 200, length_range=(12, 16)) -> List[str]:
    sequences = []
    for _ in range(n):
        L = random.randint(*length_range)
        seq = "".join(random.choice(AMINO_ALPHABET) for _ in range(L))
        sequences.append(seq)
    return sequences


def ensure_dataset() -> List[str]:
    if DATA_PATH.exists():
        sequences = []
        with DATA_PATH.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                sequences.append(row["cdr3aa"])
        print(f"Loaded {len(sequences)} CDR3 sequences from {DATA_PATH}")
        return sequences

    # Otherwise, generate synthetic data
    sequences = generate_synthetic_cdr3()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cdr3aa"])
        for s in sequences:
            writer.writerow([s])
    print(f"No dataset found; generated {len(sequences)} synthetic CDR3 sequences at {DATA_PATH}")
    return sequences


def hamming(a: str, b: str) -> int:
    assert len(a) == len(b)
    return sum(1 for x, y in zip(a, b) if x != y)


def compute_distance_stats(sequences: List[str], max_pairs: int = 10_000):
    # Filter to equal-length subset (most CDR3s are within a narrow length band)
    if not sequences:
        raise ValueError("No CDR3 sequences available")

    # Pick the dominant length
    lengths, counts = np.unique([len(s) for s in sequences], return_counts=True)
    dominant_len = lengths[np.argmax(counts)]
    same_len = [s for s in sequences if len(s) == dominant_len]

    if len(same_len) < 2:
        raise ValueError("Not enough same-length CDR3s to compute distances")

    print(f"Using {len(same_len)} sequences of length {dominant_len} aa for distance stats.")

    # Sample random pairs
    n_pairs = min(max_pairs, len(same_len) * (len(same_len) - 1) // 2)
    distances = []
    for _ in range(n_pairs):
        a, b = random.sample(same_len, 2)
        distances.append(hamming(a, b))

    distances = np.array(distances)
    print("\nHamming distance statistics (same-length CDR3 pairs):")
    print(f"- Mean:      {distances.mean():.2f}")
    print(f"- Std dev:   {distances.std():.2f}")
    print(f"- Min:       {distances.min():.0f}")
    print(f"- Max:       {distances.max():.0f}")
    for q in [0.01, 0.05, 0.10]:
        print(f"- {int(q*100)}th pct: {np.quantile(distances, q):.0f}")

    # Rough "code distance" proxy: lower tail of the distribution
    approx_d_min = np.quantile(distances, 0.01)
    print(f"\nApproximate biological code distance (1st percentile): d ≈ {approx_d_min:.0f}")


def main():
    sequences = ensure_dataset()
    compute_distance_stats(sequences)


if __name__ == "__main__":
    main()
