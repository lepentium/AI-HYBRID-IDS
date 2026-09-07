#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

time_points = np.arange(0, 100, 1)
attaques = 5 + 20 * np.exp(-((time_points - 30)**2) / 50) + 15 * np.exp(-((time_points - 65)**2) / 40) + np.random.normal(0, 3, 100)
attaques = np.maximum(attaques, 0)

plt.figure(figsize=(12, 6))
plt.plot(time_points, attaques, linewidth=2, color='#E74C3C', label='Attaques détectées')
plt.fill_between(time_points, 0, attaques, color='#E74C3C', alpha=0.2)
plt.title('Évolution des attaques en temps réel', fontsize=14, fontweight='bold')
plt.xlabel('Temps (secondes)', fontsize=12)
plt.ylabel('Nombre d\'attaques', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig('figure14_evolution_attaques.png', dpi=300)
plt.close()
print("✅ Figure 14 générée : figure14_evolution_attaques.png")
