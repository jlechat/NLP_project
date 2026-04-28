"""
Code fait sur la base de fonctions de Jonas, légérement amélioré. 
"""
# imports : 
from cleaning_data.processing import check_arbre, load_corpus, load_metadata, enrich_with_ed_flag, final_cleaning, stopwords
from dataviz.visualisation import plot_year_evolution
import os, re, unicodedata, textwrap
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd 
import spacy

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
    "Action Française", 
    "Groupe Action Jeunesse", 
    "Groupe Union Défense"
}
NLP = spacy.load('fr_core_news_sm', disable=['parser'])

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
plot_year_evolution(df_ed)
ALL_SW = stopwords()
df_ed_clean = final_cleaning(df_ed, NLP, ALL_SW)
print(df_ed_clean.head())

row = df_ed_clean.iloc[0]

print(f"\n--- Exemple ({row['filename']}) ---")
print("ORIGINAL :")
print(textwrap.fill(row['text'][:400], 90))
print("\nAPRÈS NETTOYAGE + LEMMATISATION :")
print(textwrap.fill(row['text_lemmatized'][:400], 90))

df_ed_clean.to_csv("cleaned_data.csv")

# LDA - detection du nb optimal 


# LDA - génération de topics et visualistion 



# NMF trouver le bon nb k 


# NMF - topics et visualisation 