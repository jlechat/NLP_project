## Idées de projet et de sujet pour le projet NLP 

Travailler sur le Topic modelling. évolution du discours de l'extreme droite et à quel point il est classé comme extreme d'une année à l'autre - à quel point il est extrême ou non. Quantification de la fenêtre d'overton en fine-tunant les modèles au fur et à mesure des années + modèle de classification politique (a quel point extreme) 
Essayer de comprendre si la classification de ce qui est considéré comme extrême change ? 
Sinon évaloution des sujets : sécurité puis justice sociale? 

Deuxième idée : appariton des idées écologiques, par partis, avec scores de saillance par exemple. 

Intégrer des uestions de fairness ou des questions de la mesure du calcul nécessaire. 


## A faire : 
Faire une mini-revue de littérature. Pourquoi la question est importante, méthodo NLP (ce qui existe pour le faire), et dire ce qu'on fait (supervisé, ou non, ce qui manque et des choses similaires)
et problématisation. Faire un lien entre les 3 ! 


## Problèmes 
Difficile de trouver un modèle qui estentrainé sur les données simlaires (souvent US, très réseaux sociaux). Idée - continuer avec le topic modelling mais aussi rajouter une partie avec Zero-shot learning de BERT. J'avais notamment vu un papier dessus qui fait du zero shot et few shot learning avec DeBERTa. 
On pourriat donc faire un truc comparatif entre Zero shot pur tous les ans, puis un finetuning progressif (en mode modèle baseline). A voir s'il arrive à classifier les choses de manière pertinente ! 

