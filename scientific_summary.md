# Analyse automatique des résultats

| Scénario | MWPM | BA-QEC | A-BA-QEC | Meilleure méthode |
|---|---:|---:|---:|---|
| depolarizing | 0.6300 | 0.0000 | 0.6300 | BA-QEC |
| asymmetric | 0.5150 | 0.0025 | 0.5150 | BA-QEC |
| temporal_correlation | 0.4850 | 0.0525 | 0.4850 | BA-QEC |
| burst_errors | 0.4225 | 0.0000 | 0.4225 | BA-QEC |
| progressive_drift | 0.7325 | 0.0000 | 0.7325 | BA-QEC |
| abrupt_regime_change | 0.6900 | 0.0775 | 0.6900 | BA-QEC |
| hardware_inspired | 0.4700 | 0.0000 | 0.4700 | BA-QEC |

## Ablation par moyenne

| Variante | Taux logique moyen | Latence proxy moyenne | Complexité moyenne |
|---|---:|---:|---:|
| A-BA-QEC | 0.5636 | 0.9113 | 241.37 |
| A-BA-QEC - Noise Genome | 0.5636 | 0.6977 | 247.18 |
| A-BA-QEC - Immune Memory | 0.5636 | 1.0303 | 328.23 |
| A-BA-QEC - Mutation | 0.5636 | 0.3839 | 32.00 |
| A-BA-QEC - Homeostasis | 0.5636 | 0.5682 | 105.86 |
| A-BA-QEC - Attention | 0.5636 | 0.8892 | 241.37 |

## Conclusion falsifiable

Dans cette version du protocole contrôlé, A-BA-QEC ne doit pas être déclaré supérieur automatiquement. Les valeurs ci-dessus sont les mesures de l’implémentation locale et montrent explicitement les scénarios où BA-QEC ou MWPM sont meilleurs. Une amélioration significative n’est retenue que si elle apparaît sur la métrique et le scénario pré-spécifiés, avec les mêmes seeds.
