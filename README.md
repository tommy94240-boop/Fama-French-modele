Modélisation et Analyse Factorielle : Fama-French

Ce dépôt regroupe trois projets distincts centrés sur l'implémentation et l'analyse des modèles d'évaluation des actifs de Fama et French. L'objectif de ces travaux est de démontrer à la fois la compréhension théorique de la mécanique des facteurs de risque et la capacité à développer des outils d'analyse quantitatifs interactifs.

1. "Création A à Z Fama-French 5"

Ce premier script est un projet créé de zéro à partir de 0. Il vise à reconstruire la logique du modèle à 5 facteurs afin de démystifier et d'assimiler sa mécanique mathématique.
Les paramètres calculés dans ce script ont une vocation pédagogique. En raison de l'accès limité à la totalité des bases de données institutionnelles, ils différent fortement des données officielles. Pour une analyse en conditions réelles, l'utilisation des facteurs officiels publiés sur le site de Fama et French est systématiquement privilégiée.

2. Outils d'Analyse Automatisée ("FF5" et "FF6")

Contrairement au premier projet, ces deux scripts sont des applications pratiques et automatisées destinées à l'analyse de portefeuilles réels. Ils croisent les rendements d'un portefeuille utilisateur avec les données officielles téléchargées depuis la base de données de Kenneth French.

Fonctionnalités clés :

Interface interactive : Déploiement d'un tableau de bord web local interactif grâce à la librairie Streamlit.

Modèles intégrés : Support du modèle classique à 5 facteurs et de son extension à 6 facteurs incluant la prime de tendance Momentum.

Aide à la décision : Exécution de la régression linéaire (via statsmodels) pour calculer l'Alpha du gérant, les différents Bétas factoriels, et les indicateurs de robustesse statistique (p-value, R² ajusté, F-statistic).

Interprétation : L'outil intègre des modules explicatifs pour traduire les résultats mathématiques en véritables biais de gestion (Value vs Growth, exposition aux Small Caps...)