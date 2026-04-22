# imports : 
from cleaning_data.processing import check_arbre, parse_filename, load_corpus, load_metadata, enrich_with_ed_flag
import os, re, unicodedata, textwrap
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd 


PROJECT_ROOT   = Path('.')
TEXT_FILES_DIR = PROJECT_ROOT / 'data' / 'text_files'
YEARS          = [1973, 1978, 1981, 1988, 1993]
META_PATH = 'data/meta_data.csv'  
ED_PATH = "data/liste_complete_extreme_droite.csv"
# dico partis 
ED_PARTIS = {
    # Front National et variantes
    'Front national',
    'Front National',
    'Front national pour l\'unité française',
    'Front National pour l\'Unité Française',
    'Front national de la jeunesse',
    'Front national populaire',                                                                                                                              

    # Parti des Forces Nouvelles (rival du FN en 1981, même famille)
    'Parti des forces nouvelles',
    'Parti des Forces Nouvelles',
    'PFN',

    # Autres étiquettes d'extrême droite de la période
    'Rassemblement national',
    'Ordre nouveau',
    'Mouvement nationaliste révolutionnaire',
    'Faisceaux nationalistes européens',
    'Parti nationaliste français',
    'Rassemblement des forces nationales',
    "Rassemblement pour les libertés et la patrie", 
    "Action Française"
}

# def main():
#     print("Hello from nlp-project!")


# if __name__ == "__main__":
#     main()

check_arbre(PROJECT_ROOT, YEARS, TEXT_FILES_DIR)

df_all = load_corpus(TEXT_FILES_DIR, YEARS)

# Quelques statistiques de base
print(f"\n Corpus total : {len(df_all)} professions de foi")
print("\nLongueur des textes (caractères) :")
print(df_all.groupby('year')['text_length']
      .describe()[['min','mean','max']].round(0))



df_meta = load_metadata(path = META_PATH)

df_full = enrich_with_ed_flag(df_all, df_meta, ED_PATH, ED_PARTIS)
# au cas où : 
# df_full.to_csv("full_dataset.csv")

df_ed = df_full[df_full["is_ed"]==1]

# ── 6. Visualisation ──────────────────────────────────────────────────────────
# fig, axes = plt.subplots(1, 2, figsize=(13, 4))
# colors = ['#2c7bb6', '#d7191c', '#fdae61']

# counts = df_ed['year'].value_counts().sort_index()
# counts.plot(kind='bar', ax=axes[0], color=colors)
# axes[0].set_title('Nb de PF extrême droite par année', fontweight='bold')
# axes[0].set_xlabel('Année') ; axes[0].set_ylabel('Nb documents')
# axes[0].tick_params(axis='x', rotation=0)
# for i, v in enumerate(counts):
#     axes[0].text(i, v + 0.3, str(v), ha='center', fontweight='bold')

# for year, color in zip([1973, 1978, 1981, 1988, 1993], colors):
#     sub = df_ed[df_ed['year'] == year]['text_length']
#     if len(sub) > 0:
#         axes[1].hist(sub, bins=30, alpha=0.6, label=str(year), color=color)
# axes[1].set_title('Distribution des longueurs de texte', fontweight='bold')
# axes[1].set_xlabel('Longueur (caractères)') ; axes[1].set_ylabel('Fréquence')
# axes[1].legend()

# plt.tight_layout()
# plt.savefig('corpus_overview.png', dpi=150, bbox_inches='tight')
# plt.show()
