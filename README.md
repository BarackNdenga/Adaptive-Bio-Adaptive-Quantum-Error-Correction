# A-BA-QEC

## Adaptive Bio-Adaptive Quantum Error Correction

**Auteur et responsable du projet : Barack Ndenga**  
**Branche expérimentale : `experimental/a-baqec`**  
**Licence : MIT**

A-BA-QEC est une architecture expérimentale de décodage quantique adaptatif inspirée de mécanismes d’apprentissage et de régulation des systèmes immunitaires. Le projet étend un prototype BA-QEC existant sans supprimer son implémentation originale. L’objectif est d’étudier, de manière reproductible et falsifiable, si l’observation dynamique du bruit, la mémoire des stratégies, l’évolution clonale et le contrôle du budget de calcul peuvent améliorer le décodage sous bruit non stationnaire.

> **Statut scientifique.** La version actuelle est fonctionnelle, testée et reproductible, mais elle ne démontre pas encore de supériorité d’A-BA-QEC sur les baselines dans le protocole contrôlé fourni. Les résultats négatifs sont conservés et documentés ; aucune amélioration n’est revendiquée sans mesure expérimentale correspondante.

## Architecture

La boucle adaptative suit le flux suivant :

```text
Syndrome
   ↓
Noise Genome Engine
   ↓
Artificial Immune Memory
   ↓
Syndrome Attention Engine
   ↓
Candidate Corrections
   ↓
Adaptive MWPM Response
   ↓
Correction and Evaluation
   ↓
Memory Reinforcement / Forgetting
   ↓
Clonal Mutation / Expansion
   ↺
```

Le génome dynamique du bruit est représenté par :

\[
G(t)=[P_X(t),P_Y(t),P_Z(t),C_s(t),C_t(t),D_t(t)].
\]

La mémoire immunitaire utilise une mise à jour de la forme :

\[
M(t)=\lambda M(t-1)+(1-\lambda)R(t),
\]

où `R(t)` est le score de résultat de la stratégie observée. Le paramètre `λ` est ajusté lorsque le régime de bruit devient instable afin d’accélérer l’oubli des stratégies obsolètes.

## Composants principaux

| Composant | Emplacement | Fonction |
|---|---|---|
| Noise Genome Engine | `src/a_ba_qec/noise_genome.py` | Estimation de `Px`, `Py`, `Pz`, des corrélations et du drift ; détection de régimes |
| Artificial Immune Memory | `src/a_ba_qec/immune_memory.py` | Mémoire court terme, mémoire long terme, confiance, renforcement et oubli |
| Clonal Evolution Engine | `src/a_ba_qec/clonal_evolution.py` | Expansion des stratégies efficaces et mutation des stratégies échouées |
| Adaptive MWPM | `src/a_ba_qec/adaptive_mwpm.py` | Adaptateur optionnel pour des poids MWPM dépendant du bruit observé |
| Adaptive Response | `src/a_ba_qec/adaptive_response.py` | Apprentissage des profils d’erreur par qubit et type X/Y/Z |
| Immune Homeostasis | `src/a_ba_qec/homeostasis.py` | Choix du niveau d’activité et du budget de candidats |
| Syndrome Attention | `src/a_ba_qec/adaptive_response.py` | Priorisation des syndromes selon leur potentiel d’information |
| Adaptive Decoder | `src/a_ba_qec/adaptive_decoder.py` | Orchestration de la boucle d’apprentissage continue |

Le décodeur BA-QEC original reste dans `src/decoder.py`. Il n’est pas remplacé par A-BA-QEC et sert de référence de non-régression.

## Résultats actuels

Le benchmark contrôlé compare MWPM, BA-QEC et A-BA-QEC sur sept scénarios : bruit dépolarisant, bruit asymétrique, bruit temporellement corrélé, burst errors, drift progressif, changement brutal de régime et scénario inspiré des données hardware présentes dans l’archive.

| Scénario | MWPM | BA-QEC | A-BA-QEC | Meilleure méthode mesurée |
|---|---:|---:|---:|---|
| Dépolarisant | 0.6300 | 0.0000 | 0.6300 | BA-QEC |
| Asymétrique | 0.5150 | 0.0025 | 0.5150 | BA-QEC |
| Corrélation temporelle | 0.4850 | 0.0525 | 0.4850 | BA-QEC |
| Burst errors | 0.4225 | 0.0000 | 0.4225 | BA-QEC |
| Drift progressif | 0.7325 | 0.0000 | 0.7325 | BA-QEC |
| Changement brutal | 0.6900 | 0.0775 | 0.6900 | BA-QEC |
| Hardware-inspired | 0.4700 | 0.0000 | 0.4700 | BA-QEC |

Ces valeurs proviennent du protocole contrôlé local et ne constituent pas une nouvelle expérience hardware ni une validation complète d’un code de surface. La version actuelle montre donc que l’architecture adaptative est opérationnelle mais que le lien entre apprentissage du bruit et qualité de correction doit encore être amélioré.

## Étude d’ablation

L’étude obligatoire compare A-BA-QEC complet aux variantes suivantes : retrait du Noise Genome, retrait de la mémoire immunitaire, retrait de la mutation, retrait de l’homéostasie et retrait de l’attention.

| Variante | Taux logique moyen | Latence proxy moyenne | Complexité proxy moyenne |
|---|---:|---:|---:|
| A-BA-QEC | 0.5636 | 0.9113 | 241.37 |
| Sans Noise Genome | 0.5636 | 0.6977 | 247.18 |
| Sans Immune Memory | 0.5636 | 1.0303 | 328.23 |
| Sans Mutation | 0.5636 | 0.3839 | 32.00 |
| Sans Homeostasis | 0.5636 | 0.5682 | 105.86 |
| Sans Attention | 0.5636 | 0.8892 | 241.37 |

L’ablation ne montre pas encore d’effet sur le taux logique moyen. Elle indique en revanche que certains composants modifient fortement le coût computationnel. Cette observation doit être interprétée comme un résultat négatif et comme une indication pour la prochaine itération scientifique.

## Installation

Le projet requiert Python 3.8 ou une version ultérieure. Les dépendances principales sont NumPy, Matplotlib, Stim, PyMatching et tqdm.

```bash
python3 -m pip install -r requirements.txt
```

Pour les tests et le développement :

```bash
python3 -m pip install -e ".[dev]"
```

L’intégration IBM/Qiskit est optionnelle et n’est pas nécessaire pour exécuter les benchmarks locaux :

```bash
python3 -m pip install qiskit qiskit-ibm-runtime
```

Le script matériel `realqtest_1121.py` est un export historique de notebook et ne doit pas être exécuté automatiquement. Aucun accès hardware n’est déclenché par les commandes de benchmark ci-dessous.

## Reproduction en une commande

Depuis la racine du dépôt :

```bash
python3 run_benchmark.py
```

Cette commande produit :

```text
results/benchmark_results.json
results/benchmark_results.csv
```

Pour l’étude d’ablation :

```bash
python3 run_ablation.py
```

Pour générer les graphiques :

```bash
python3 benchmarks/plot_results.py
```

Les figures sont écrites dans `figures/` : taux d’erreur logique, latence proxy, complexité proxy, robustesse au drift et étude d’ablation.

Pour exécuter la suite de tests :

```bash
python3 -m pytest
```

La suite actuelle couvre le décodeur original, le génome du bruit, la mémoire immunitaire, l’évolution clonale, l’homéostasie, l’attention et l’adaptateur MWPM.

## Reproductibilité

Les paramètres expérimentaux sont centralisés dans `configs/benchmark.json`. Le seed principal est `20260817`, le benchmark utilise 400 tirs par scénario et 16 qubits binaires dans le protocole contrôlé.

Les métriques de latence et de mémoire enregistrées dans les fichiers JSON sont des proxies déterministes afin que les artefacts soient reproductibles indépendamment de la machine. Les temps muraux et les pics mémoire propres à une machine doivent être mesurés séparément dans une étude de performance dédiée.

Les instructions détaillées se trouvent dans `docs/REPRODUCIBILITY.md`. Le manuscrit scientifique complet, avec graphiques et discussion des limites, se trouve dans `docs/A_BA_QEC_scientific_article.md`.

## Protection du projet original

Le dépôt original a été conservé dans son architecture existante. A-BA-QEC est isolé sous `src/a_ba_qec/`, tandis que `src/decoder.py`, les scripts historiques, les notebooks et les données restent présents.

La branche expérimentale est :

```text
experimental/a-baqec
```

La branche `main` conserve l’état de référence enregistré avant la finalisation des extensions expérimentales. Le test `tests/test_original_regression.py` vérifie que le décodeur BA-QEC original reste importable, déterministe et fonctionnel.

## Données et provenance

L’archive contient des fichiers pickle et des images associés à une exécution hardware historique. Leur présence dans le dépôt est documentée, mais les résultats du benchmark A-BA-QEC ne doivent pas être présentés comme une nouvelle exécution IBM. Le scénario `hardware-inspired` est une expérience locale contrôlée inspirée par la structure non uniforme décrite dans les données disponibles.

## Références techniques

Les outils scientifiques utilisés dans l’écosystème du projet comprennent [Stim](https://doi.org/10.22331/q-2021-07-06-497), simulateur de circuits stabilisateurs, et [PyMatching](https://arxiv.org/abs/2105.13082), bibliothèque de décodage MWPM. Une revue récente des algorithmes de décodage des codes de surface est disponible dans [Decoding algorithms for surface codes](https://doi.org/10.22331/q-2024-10-10-1498).

## Développement et contributions

Les contributions doivent préserver l’exécution du BA-QEC original, fournir des seeds déterministes pour les nouvelles expériences et distinguer clairement les résultats mesurés des hypothèses. Toute amélioration proposée doit être évaluée sur l’ensemble des scénarios prévus, y compris les scénarios défavorables à A-BA-QEC.

Les prochaines priorités scientifiques sont une intégration Stim/PyMatching avec mapping physique vérifié, une séparation stricte entre fenêtre d’apprentissage et fenêtre de test, une évaluation multi-seeds et une mesure de performance temps réel sur des circuits de surface code correctement définis.

## Auteur

**Barack Ndenga**  
A-BA-QEC — Adaptive Bio-Adaptive Quantum Error Correction
