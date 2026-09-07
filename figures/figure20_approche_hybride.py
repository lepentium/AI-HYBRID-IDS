#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 6))

rect_rf = patches.Rectangle((1, 3.5), 2, 1.2, linewidth=2, edgecolor='black', facecolor='#4A90D9', alpha=0.7)
ax.add_patch(rect_rf)
ax.text(2, 4.1, 'Random Forest', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_xgb = patches.Rectangle((3.5, 3.5), 2, 1.2, linewidth=2, edgecolor='black', facecolor='#5BA3E6', alpha=0.7)
ax.add_patch(rect_xgb)
ax.text(4.5, 4.1, 'XGBoost', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_lgb = patches.Rectangle((6, 3.5), 2, 1.2, linewidth=2, edgecolor='black', facecolor='#6BB5F2', alpha=0.7)
ax.add_patch(rect_lgb)
ax.text(7, 4.1, 'LightGBM', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_if = patches.Rectangle((9, 3.5), 2, 1.2, linewidth=2, edgecolor='black', facecolor='#2ECC71', alpha=0.7)
ax.add_patch(rect_if)
ax.text(10, 4.1, 'Isolation Forest', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(5, 2.2), xytext=(2, 3.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(5, 2.2), xytext=(4.5, 3.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(5, 2.2), xytext=(7, 3.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(5, 2.2), xytext=(10, 3.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='dashed'))

rect_vote = patches.Rectangle((3.5, 1.2), 3, 0.8, linewidth=2, edgecolor='black', facecolor='#F39C12', alpha=0.7)
ax.add_patch(rect_vote)
ax.text(5, 1.6, 'VOTE MAJORITAIRE', fontsize=11, fontweight='bold', va='center', ha='center', color='white')

rect_dec = patches.Rectangle((4, 0), 2, 1.0, linewidth=2, edgecolor='black', facecolor='#E74C3C', alpha=0.7)
ax.add_patch(rect_dec)
ax.text(5, 0.5, 'Décision finale\n(Attack / Normal)', fontsize=11, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(5, 1.2), xytext=(5, 2.0), arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.set_xlim(0, 12)
ax.set_ylim(0, 5.5)
ax.axis('off')
ax.set_title('Approche hybride : 3 supervisés + 1 non supervisé', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure20_approche_hybride.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 20 générée : figure20_approche_hybride.png")
