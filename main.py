# imports : 
from cleaning_data.processing import check_arbre, parse_filename, load_corpus, load_metadata


PROJECT_ROOT   = Path('.')
TEXT_FILES_DIR = PROJECT_ROOT / 'data' / 'text_files'
YEARS          = [1973, 1978, 1981, 1988, 1993]
META_PATH = 'data/meta_data.csv'  

def main():
    print("Hello from nlp-project!")


if __name__ == "__main__":
    main()

check_arbre()

df_all = load_corpus(TEXT_FILES_DIR, YEARS)

# Quelques statistiques de base
print(f"\n Corpus total : {len(df_all)} professions de foi")
print("\nLongueur des textes (caractères) :")
print(df_all.groupby('year')['text_length']
      .describe()[['min','mean','max']].round(0))