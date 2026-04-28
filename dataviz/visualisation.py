""" 
Fonctions pour produire les graphiques, utiles aux analyses. 
"""
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
import os, re, unicodedata, textwrap
import numpy as np
import matplotlib.ticker as mtick

def plot_year_evolution(df_ed, save = False): 

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Palette de 5 couleurs (nuances de rouge, orange, bleu clair, bleu moyen, bleu foncé)
    # Cette palette suit la logique ColorBrewer "RdYlBu"
    colors = ['#d7191c', '#fdae61', '#abd9e9', '#4575b4', '#313695']

    # Liste des années cibles
    years_list = [1973, 1978, 1981, 1988, 1993]

    # --- Graphique 1 : Barres ---
    counts = df_ed['year'].value_counts().sort_index()
    # On s'assure que le nombre de couleurs correspond au nombre de barres
    counts.plot(kind='bar', ax=axes[0], color=colors[:len(counts)])

    axes[0].set_title('Nb de PF extrême droite par année', fontweight='bold')
    axes[0].set_xlabel('Année') 
    axes[0].set_ylabel('Nb documents')
    axes[0].tick_params(axis='x', rotation=0)

    for i, v in enumerate(counts):
        axes[0].text(i, v + 0.3, str(v), ha='center', fontweight='bold')

    # --- Graphique 2 : Histogrammes ---
    for year, color in zip(years_list, colors):
        sub = df_ed[df_ed['year'] == year]['text_length']
        if len(sub) > 0:
            axes[1].hist(sub, bins=30, alpha=0.5, label=str(year), color=color, edgecolor='white')

    axes[1].set_title('Distribution des longueurs de texte', fontweight='bold')
    axes[1].set_xlabel('Longueur (caractères)') 
    axes[1].set_ylabel('Fréquence')
    axes[1].legend(title="Années")
    plt.tight_layout()
    if save: 
        plt.savefig('corpus_overview_yearly.png', dpi=150, bbox_inches='tight')
    plt.show()

def print_preview_random(df_ed, nb=3) : 
    print("\n" + "="*65)
    print("APERÇU: " + nb + " exemples de PF extrême droite identifiées")
    print("="*65)
    for _, row in df_ed.sample(n=min(nb, len(df_ed)), random_state=42).iterrows():
        print(f"\n[{row['year']} | {row.get('titulaire-prenom','')} "
            f"{row.get('titulaire-nom','')} | Parti : {row['titulaire-liste']}]")
        print(textwrap.fill(row['text'][:400], width=88))


