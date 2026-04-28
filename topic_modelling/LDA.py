import pandas as pd 
import os, re, unicodedata, textwrap
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def check_nb_clusters(df_ed, topics_range = [3, 5, 6, 7,8, 10, 12 ,15, 20]):
        
    # 1. Vectorisation (inchangée)
    N_FEATURES = 2000
    tf_vectorizer = CountVectorizer(
        max_features=N_FEATURES,
        stop_words=list(ALL_SW),
        min_df=2, max_df=0.9,
        ngram_range=(1, 2)
    )
    tf_matrix = tf_vectorizer.fit_transform(df_ed['text_lemmatized'])

    # 2. Recherche du nombre optimal de topics
     # Liste des valeurs à tester
    perplexity_scores = []

    for n_topics in topics_range:
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=10, # On réduit un peu les itérations pour gagner du temps en phase de test
            learning_method='batch',
            random_state=42,
            n_jobs=-1
        )
        lda.fit(tf_matrix)
        perplexity_scores.append(lda.perplexity(tf_matrix))
        print(f"Calcul terminé pour n_topics = {n_topics}")

    # 3. Visualisation
    plt.figure(figsize=(10, 6))
    plt.plot(topics_range, perplexity_scores, marker='o', linestyle='-', color='b')
    plt.title("Évolution de la Perplexity selon le nombre de topics")
    plt.xlabel("Nombre de Topics")
    plt.ylabel("Perplexity")
    plt.grid(True)
    plt.show()