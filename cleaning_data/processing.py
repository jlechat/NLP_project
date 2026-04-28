import os, re, unicodedata, textwrap
from pathlib import Path
from collections import Counter
import spacy 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import re
import unicodedata


def check_arbre(PROJECT_ROOT, YEARS, TEXT_FILES_DIR): 
# Affichage de l'arborescence et du nombre de fichiers
    print(f"Racine du projet : {PROJECT_ROOT.resolve()}")
    for year in YEARS:
        p = TEXT_FILES_DIR / str(year) / 'legislatives'
        if p.exists():
            n = len(list(p.glob('*.txt')))
            print(f"  {year}/legislatives/ → {n} fichiers .txt")
        else:
            print(f"  année {p} introuvable !")

def parse_filename(filepath):
    """
    Mise en forme du nom de fichier Archelec pour créer des méta données :
      EL134_L_1981_06_001_01_1_PF_01.txt
      EL134_L_1981_06_02A_01_1_PF_01.txt  ← Corse (dep alphanumérique)
      EL134_L_1981_06_013_10_1_BV_pdfmasterocr.txt  ← ignoré (pas une PF)
    """
    name  = Path(filepath).stem
    parts = name.split('_')
    
    try:
        doc_type = parts[7]   # permet d'accéder à la catégorie PF = professions de foi
        
        # Numéro de candidat : peut être 'pdfmasterocr' pour les BV mal nommés
        # → on met None, le filtre doc_type != 'PF' les éliminera de toute façon
        try:
            candidat_num = int(parts[8])
        except (ValueError, IndexError):
            candidat_num = None

        # Département : peut être '001', '02A', '02B' (Corse)
        dep_raw = parts[4]
        if dep_raw.upper() in ('02A', '2A'):
            dep = '2A'   # Corse-du-Sud
        elif dep_raw.upper() in ('02B', '2B'):
            dep = '2B'   # Haute-Corse
        else:
            dep = int(dep_raw)   # cas normal : entier

        return {
            'archelec_id'  : parts[0],
            'election_type': parts[1],
            'year'         : int(parts[2]),
            'month'        : parts[3],
            'dep'          : dep,
            'circ'         : int(parts[5]),
            'tour'         : int(parts[6]),
            'doc_type'     : doc_type,
            'candidat_num' : candidat_num,
        }

    except (IndexError, ValueError) as e:
        print(f"Parsing échoué pour '{name}' : {e}")
        return {k: None for k in
                ['archelec_id','election_type','year','month',
                 'dep','circ','tour','doc_type','candidat_num']}

def load_corpus(text_files_dir, years):
    """
    Charge les fichiers .txt dans text_files/{année}/legislatives/
    Ne conserve que les documents de type PF (Profession de Foi).
    """
    records = []
    for year in years:
        folder = Path(text_files_dir) / str(year) / 'legislatives'
        if not folder.exists():
            print(f"Dossier manquant : {folder}") ; continue

        n_pf = n_skip = 0
        for fpath in sorted(folder.glob('*.txt')):
            meta = parse_filename(fpath)

            # On ne garde que les Professions de Foi
            if meta['doc_type'] != 'PF':
                n_skip += 1 ; continue

            # Lecture avec le bon encodage
            try:
                text = fpath.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                text = fpath.read_text(encoding='latin-1')

            text = text.strip()
            records.append({
                'filename'     : fpath.name,
                'archelec_id'  : meta['archelec_id'],
                'year'         : year,
                'dep'          : meta['dep'],
                'circ'         : meta['circ'],
                'tour'         : meta['tour'],
                'candidat_num' : meta['candidat_num'],
                'text'         : text,
                'text_length'  : len(text),
            })
            n_pf += 1

        print(f"{year} : {n_pf} PF chargées  ({n_skip} fichiers non-PF ignorés)")

    return pd.DataFrame(records)

def load_metadata(path) : 
    df_meta = pd.read_csv(path, sep=',', encoding='utf-8', low_memory=False)

    print(f"Métadonnées chargées : {len(df_meta)} lignes")
    print(f"Colonnes : {list(df_meta.columns)}\n")

    # Affichage d'une partie de la table
    print("Aperçu des colonnes 'titulaire-liste' et 'titulaire-soutien' :")
    print(df_meta[['id','titulaire-liste','titulaire-soutien']].head(5).to_string())
    return df_meta


# idnetifier les fichiers comme les fichier d'extrême droite : 
def clean_text(s):
    """Normalisation : minuscules, sans accents, sans parenthèses et leur contenu."""
    if pd.isna(s):
        return ""
    s = str(s)
    # On retire le contenu entre parenthèses
    s = re.sub(r'\(.*?\)', '', s)
    # On retire les accents
    s = ''.join(c for c in unicodedata.normalize('NFKD', s)
                if unicodedata.category(c) != 'Mn')
    # On nettoie les espaces et la casse
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def get_ed_reference_set(csv_path, initial_dico):
    """Prépare l'ensemble des partis de référence nettoyés."""
    try:
        df_csv = pd.read_csv(csv_path)
        csv_list = df_csv.iloc[:, 0].tolist()
    except FileNotFoundError:
        print(f"Attention : {csv_path} introuvable, utilisation du dico initial uniquement.")
        csv_list = []
        
    full_list = list(initial_dico) + csv_list
    reference_set = {clean_text(p) for p in full_list if pd.notna(p)}
    reference_set.discard("")
    return reference_set

# --- 2. Fonction principale de transformation ---

def enrich_with_ed_flag(df_all, df_meta, csv_path, initial_dico):
    """
    Transforme df_all en lui ajoutant les métadonnées et la colonne binaire is_ed.
    """
    # création de la colonne 'id' dans df_all (nom_du_doc.txt -> nom_du_doc)
    # .str[:-4] est très efficace pour retirer les 4 derniers caractères (.txt)
    df_all['id'] = df_all['filename'].str.replace('.txt', '', regex=False)

    # Jointure avec df_meta
    # On s'assure que df_meta a aussi une colonne 'id'
    df_final = df_all.merge(df_meta, on='id', how='left')

    # Préparation de la référence ED - merge du csv scrapé et de la liste à la mano 
    ed_reference = get_ed_reference_set(csv_path, initial_dico)

    #  Création de la colonne binaire is_ed
    # On nettoie temporairement pour la comparaison
    temp_liste = df_final['titulaire-liste'].apply(clean_text)
    temp_soutien = df_final['titulaire-soutien'].apply(clean_text)

    #  verification dans le set de référence
    mask_ref = (temp_liste.isin(ed_reference)) | (temp_soutien.isin(ed_reference))
    
    # Sécurité pour les variantes textuelles (Front National, etc.)
    mask_keywords = (temp_liste.str.contains('front national|parti des forces nouvelles', na=False)) | \
                    (temp_soutien.str.contains('front national|parti des forces nouvelles', na=False))

    # Attribution de la valeur binaire (1 si ED, 0 sinon)
    df_final['is_ed'] = (mask_ref | mask_keywords).astype(int)

    print(f"Enrichissement terminé.")
    print(f"Nombre de documents marqués ED : {df_final['is_ed'].sum()} sur {len(df_final)}")
    
    return df_final


def clean_ocr(text):
    """
    Nettoyage des artefacts spécifiques aux professions de foi Archelec numérisées.
    """
    # 1. Suppression des éléments  "Sciences Po / CEVIPOF"
    text = re.sub(r'sciences\s*po\s*/\s*fonds\s*cevipof', ' ', text, flags=re.I)
    text = re.sub(r'sciences\s*po', ' ', text, flags=re.I)
    text = re.sub(r'fonds\s*cevipof', ' ', text, flags=re.I)

    # 2. Suppression des symboles de cases à cocher
    text = re.sub(r'[☐□▢▪▫◻◼■●]', ' ', text)

    # 3. Suppressions des lignes de séparation graphique
    text = re.sub(r'[-=_*·]{3,}', ' ', text)

    # 4. Suppression des mentions d'imprimerie en fin de ligne
    text = re.sub(r'\bIMP[_\s][\w\s\.]+', ' ', text, flags=re.I)
    text = re.sub(r'\bIMPRIME[RIE\s]+[\w\s\.]+', ' ', text, flags=re.I)
    text = re.sub(r'\bPAPIER\s+R[EÉ]CUP[EÉ]R[EÉ][\w\s]+', ' ', text, flags=re.I)

    # 5. Suppression des numéros de page isolés
    text = re.sub(r'^\s*\d{1,2}\s*$', '', text, flags=re.M)

    # 6. Suppression des caractères non imprimables (sauf newline)
    text = ''.join(c for c in text
                   if unicodedata.category(c)[0] != 'C' or c == '\n')

    # 7. Suppression des espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Stopwords 

def stopwords(stopword_path="data/stopwords.csv", spacy_mod="fr_core_news_sm"): 

    nlp = spacy.load(spacy_mod, disable=['parser'])

    # on récupère les stop words
    SW_SPACY = set(nlp.Defaults.stop_words)

    df = pd.read_csv(stopword_path)

    SW_CSV = set(df.iloc[:, 0].astype(str).str.strip().str.lower())

    ALL_SW = SW_SPACY | SW_CSV

    return ALL_SW


def lemmatize(text, nlp, stopwords, mode='lemma'):
    doc = nlp(text[:100_000])
    
    if mode == 'ner':
        # On extrait uniquement les entités nommées (en minuscules)
        return ' '.join([ent.text.lower() for ent in doc.ents if ent.label_ in ['PER', 'LOC', 'ORG']])
    
    # Mode par défaut : lemmatisation classique
    return ' '.join(
        tok.lemma_.lower()
        for tok in doc
        if tok.is_alpha
        and not tok.is_stop
        and not tok.is_punct
        and len(tok.lemma_) >= 3
        and tok.lemma_.lower() not in stopwords
    )


def final_cleaning(df_ed, nlp, stopwords):
    df_ed['text_clean'] = df_ed['text'].apply(clean_ocr)

    print(f"Traitement de {len(df_ed)} documents...")
    
    # Génération de la colonne Lemmes
    df_ed['text_lemmatized'] = [
        lemmatize(t, nlp, stopwords, mode='lemma') for t in df_ed['text_clean']
    ]
    

    return df_ed