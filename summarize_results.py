import json
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / 'results' / 'benchmark_results.json').read_text())
abl = json.loads((root / 'results' / 'ablation_results.json').read_text())
lines = ['# Analyse automatique des résultats', '', '| Scénario | MWPM | BA-QEC | A-BA-QEC | Meilleure méthode |', '|---|---:|---:|---:|---|']
for scenario in dict.fromkeys(row['scenario'] for row in rows):
    vals = {row['method']: row['logical_error_rate'] for row in rows if row['scenario'] == scenario}
    best = min(vals, key=vals.get)
    lines.append(f"| {scenario} | {vals['MWPM']:.4f} | {vals['BA-QEC']:.4f} | {vals['A-BA-QEC']:.4f} | {best} |")
lines += ['', '## Ablation par moyenne', '', '| Variante | Taux logique moyen | Latence proxy moyenne | Complexité moyenne |', '|---|---:|---:|---:|']
for variant in dict.fromkeys(row['variant'] for row in abl):
    subset = [row for row in abl if row['variant'] == variant]
    avg = lambda key: sum(row[key] for row in subset) / len(subset)
    lines.append(f"| {variant} | {avg('logical_error_rate'):.4f} | {avg('decoding_latency_ms'):.4f} | {avg('computational_complexity'):.2f} |")
lines += ['', '## Conclusion falsifiable', '', 'Dans cette version du protocole contrôlé, A-BA-QEC ne doit pas être déclaré supérieur automatiquement. Les valeurs ci-dessus sont les mesures de l’implémentation locale et montrent explicitement les scénarios où BA-QEC ou MWPM sont meilleurs. Une amélioration significative n’est retenue que si elle apparaît sur la métrique et le scénario pré-spécifiés, avec les mêmes seeds.']
(root / 'results' / 'scientific_summary.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
