"""
simulations/clonal_benchmark.py

Toy clonal expansion benchmark on synthetic CDR3 sequences.

This script:
- loads or generates CDR3 sequences via `data/sample_cdr3.csv`,
- selects a dominant length subset,
- simulates repeated antigen exposures where higher-affinity clones
  undergo stronger expansion,
- reports how concentrated the final clone size distribution becomes
  (e.g., what fraction of the total population is carried by the top 1/5/10%).

This is a cartoon of immune clonal expansion, intended to mirror the
"weight boosting" used in the BA-QEC decoder.
"""

import csv
import random
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = Path("data") / "sample_cdr3.csv"
RESULTS_PATH = Path("results") / "clonal_expansion_benchmark.png"

AMINO_ALPHABET = "ACDEFGHIKLMNPQRSTVWY"


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


def pick_same_length_subset(sequences: List[str]) -> List[str]:
    lengths, counts = np.unique([len(s) for s in sequences], return_counts=True)
    dominant_len = lengths[np.argmax(counts)]
    same_len = [s for s in sequences if len(s) == dominant_len]
    print(f"Using {len(same_len)} sequences of length {dominant_len} aa for clonal benchmark.")
    return same_len


def simulate_clonal_expansion(sequences: List[str], n_rounds: int = 10, seed: int = 0):
    rng = np.random.default_rng(seed)
    L = len(sequences[0])

    # Pick one random "antigen" epitope
    antigen = "".join(rng.choice(list(AMINO_ALPHABET)) for _ in range(L))

    # Hamming distances and affinities
    dists = np.array([hamming(s, antigen) for s in sequences])
    # Convert to [0,1]: higher affinity for smaller distance
    affinities = 1.0 - dists / L

    # Initial clone sizes
    sizes = np.ones(len(sequences), dtype=float)

    # Expansion parameters
    gamma = 3.0  # strength of expansion
    for _ in range(n_rounds):
        # Simple multiplicative update with global normalisation
        growth = 1.0 + gamma * np.clip(affinities, 0.0, 1.0)
        sizes *= growth
        sizes /= sizes.sum()  # keep total mass ~1

    return sizes, affinities


def summarise_distribution(sizes: np.ndarray):
    sorted_sizes = np.sort(sizes)[::-1]
    cum_sizes = np.cumsum(sorted_sizes)

    n = len(sorted_sizes)

    def frac_top(k_frac):
        k = max(1, int(n * k_frac))
        return cum_sizes[k - 1]

    print("\nFinal clone size concentration:")
    print(f"- Top 1% of clones carry   ~{frac_top(0.01)*100:5.1f}% of total mass")
    print(f"- Top 5% of clones carry   ~{frac_top(0.05)*100:5.1f}% of total mass")
    print(f"- Top 10% of clones carry  ~{frac_top(0.10)*100:5.1f}% of total mass")

    return sorted_sizes, cum_sizes


def plot_distribution(sorted_sizes: np.ndarray, cum_sizes: np.ndarray):
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(6, 4))
    x = np.arange(1, len(sorted_sizes) + 1)

    ax1.plot(x, sorted_sizes, label="Clone size (sorted)")
    ax1.set_xlabel("Clone rank")
    ax1.set_ylabel("Relative size")

    ax2 = ax1.twinx()
    ax2.plot(x, cum_sizes, linestyle="--", label="Cumulative mass")
    ax2.set_ylabel("Cumulative fraction")

    ax1.set_xscale("log")
    ax1.set_title("Toy clonal expansion benchmark")

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="lower right")

    fig.tight_layout()
    fig.savefig(RESULTS_PATH, dpi=200)
    print(f"Saved clonal expansion figure to {RESULTS_PATH}")


def main():
    sequences = ensure_dataset()
    same_len = pick_same_length_subset(sequences)
    sizes, _ = simulate_clonal_expansion(same_len)
    sorted_sizes, cum_sizes = summarise_distribution(sizes)
    plot_distribution(sorted_sizes, cum_sizes)


if __name__ == "__main__":
    main()
