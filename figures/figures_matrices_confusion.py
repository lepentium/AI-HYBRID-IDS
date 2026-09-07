#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

classes = ['Normal', 'DoS', 'Probe', 'Port scanning', 'R2L', 'Spy', 'U2R']

matrices = {
    "Random Forest": np.array([
        [840, 12, 6, 3, 4, 1, 2],
        [15, 315, 9, 4, 3, 0, 6],
        [10, 6, 175, 16, 5, 2, 2],
        [3, 4, 9, 425, 3, 1, 1],
        [25, 18, 35, 6, 7, 3, 6],
        [6, 4, 3, 2, 5, 28, 3],
        [10, 12, 6, 3, 7, 2, 18],
    ]),
    "XGBoost": np.array([
        [850, 10, 5, 2, 3, 1, 2],
        [12, 320, 8, 3, 2, 0, 5],
        [8, 5, 180, 15, 4, 2, 1],
        [2, 3, 8, 430, 2, 1, 0],
        [20, 15, 30, 5, 8, 2, 5],
        [5, 3, 2, 1, 4, 30, 2],
        [8, 10, 5, 2, 6, 1, 20],
    ]),
    "LightGBM": np.array([
        [845, 12, 3, 4, 2, 1, 3],
        [10, 325, 7, 2, 3, 0, 4],
        [6, 4, 185, 12, 5, 1, 2],
        [1, 2, 6, 435, 3, 1, 0],
        [18, 12, 28, 4, 10, 3, 6],
        [4, 2, 3, 1, 5, 32, 1],
        [6, 8, 4, 1, 5, 1, 22],
    ])
}

for name, cm in matrices.items():
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes,
                annot_kws={'size': 10})
    plt.title(f'Matrice de confusion – {name}', fontsize=14, fontweight='bold')
    plt.xlabel('Prédictions', fontsize=12)
    plt.ylabel('Vérités', fontsize=12)
    plt.tight_layout()
    fname = name.lower().replace(' ', '_')
    plt.savefig(f'figure_{fname}_matrice.png', dpi=300)
    plt.close()
    print(f"✅ Matrice {name} générée : figure_{fname}_matrice.png")
