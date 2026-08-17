# A-BA-QEC — reproductibilité et statut scientifique

## Commandes

Depuis la racine du dépôt, les expériences contrôlées sont reproduites par :

```bash
python3 run_benchmark.py
python3 run_ablation.py
python3 benchmarks/plot_results.py
python3 -m pytest
```

Les résultats sont écrits dans `results/` et les figures dans `figures/`. Les seeds, le nombre de tirs, le nombre de qubits, les scénarios et les méthodes sont fixés dans `configs/benchmark.json`. Les exécutions ne soumettent aucun circuit à IBM Quantum.

## Équations implémentées

Le Noise Genome Engine produit :

\[
G(t)=[P_X(t),P_Y(t),P_Z(t),C_s(t),C_t(t),D_t(t)].
\]

La mémoire applique :

\[
M(t)=\lambda M(t-1)+(1-\lambda)R(t),
\]

avec un λ diminué lorsque l’instabilité du régime augmente. Le score d’attention est une combinaison pondérée de l’affinité, de la récurrence, de la confiance, de la corrélation spatiale, de la corrélation temporelle et du drift. Le contrôleur homéostatique convertit le taux d’erreur, le drift, l’instabilité et l’incertitude en quatre budgets : `low`, `normal`, `high` et `emergency`.

## Métriques

Le benchmark exporte le taux d’erreur physique observé, le taux d’erreur logique mesuré, une latence déterministe proxy, un proxy explicite de complexité (`nombre de candidats × nombre de qubits`), une mémoire déterministe proxy, la convergence, la vitesse d’adaptation au premier changement de régime détecté et la robustesse sur la seconde moitié des scénarios avec changement ou drift. Les temps muraux et les pics mémoire système sont volontairement exclus de l’artefact principal, car ils varient selon l’hôte ; ils doivent être mesurés séparément pour une étude de performance dédiée.

## Interprétation honnête

Le décodeur original `src/decoder.py` est un prototype de distance de Hamming sur détecteurs synthétiques. Les notebooks contiennent par ailleurs des implémentations Stim/PyMatching distinctes et parfois non déterministes. Le benchmark A-BA-QEC local est donc une plateforme contrôlée et reproductible ; il ne doit pas être présenté comme une validation de performance sur un code de surface matériel complet.

Les premiers résultats exécutés après suppression d’une fuite de cible montrent une surcharge importante de latence et de complexité pour A-BA-QEC, sans gain de taux d’erreur logique sur les sept scénarios de la version actuelle. Cette observation est conservée comme résultat négatif. Elle falsifie l’hypothèse forte selon laquelle l’adaptation actuelle améliore automatiquement le décodage. Une prochaine itération doit introduire une représentation correcte du syndrome et de la correction logique, un modèle Stim/PyMatching contrôlé par régime et une sélection calibrée sur des observations passées uniquement.

## Protection du projet original

Le fichier `src/decoder.py`, les scripts existants et les notebooks ne sont pas modifiés par l’architecture A-BA-QEC. Les nouveaux modules sont regroupés sous `src/a_ba_qec/`. L’audit et la baseline sont archivés dans `../BA_QEC_AUDIT_BASELINE.md`.
