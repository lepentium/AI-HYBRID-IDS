#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 8))

rect_table = patches.Rectangle((2, 3), 8, 4, linewidth=3, edgecolor='black', facecolor='#D3D3D3', alpha=0.3)
ax.add_patch(rect_table)
ax.text(6, 6.5, 'Table : packets', fontsize=14, fontweight='bold', va='center', ha='center')

columns = [
    {"name": "id (INTEGER)", "pk": True},
    {"name": "timestamp (TEXT)", "pk": False},
    {"name": "src_ip (TEXT)", "pk": False},
    {"name": "dst_ip (TEXT)", "pk": False},
    {"name": "protocol (TEXT)", "pk": False},
    {"name": "src_port (INTEGER)", "pk": False},
    {"name": "dst_port (INTEGER)", "pk": False},
    {"name": "packet_size (INTEGER)", "pk": False},
    {"name": "ttl (INTEGER)", "pk": False},
    {"name": "flags (TEXT)", "pk": False},
    {"name": "ml_prediction (TEXT)", "pk": False},
    {"name": "anomaly (INTEGER)", "pk": False},
    {"name": "correlation_score (REAL)", "pk": False},
    {"name": "llm_report (TEXT)", "pk": False},
]

for i, col in enumerate(columns):
    y = 6 - (i+1) * 0.35
    x = 2.5
    color = '#F39C12' if col['pk'] else '#FFFFFF'
    rect = patches.Rectangle((x, y-0.12), 7, 0.3, linewidth=1, edgecolor='gray', facecolor=color)
    ax.add_patch(rect)
    ax.text(x+0.2, y, col['name'], fontsize=9, va='center', ha='left')
    if col['pk']:
        ax.text(8.8, y, 'PK', fontsize=8, va='center', ha='right', color='red', fontweight='bold')

ax.text(6, 1.5, 'Base de données SQLite : ids.db', fontsize=12, fontweight='bold', va='center', ha='center')
ax.text(6, 1.0, 'Stockage des alertes et des rapports LLM', fontsize=10, va='center', ha='center', style='italic')

ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_title('Architecture de la base de données SQLite', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure22_sqlite_architecture.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 22 générée : figure22_sqlite_architecture.png")
