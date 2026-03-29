import statsmodels.api as sm
import pandas as pd
import numpy as np
import streamlit as st

#Voici la version à 6 facteurs du modèle de Fama-French, on ajoute le facteur momentum c'est à dire la tendance des actifs qui montent ont tendancent à continuer à monter


#Voici le lien pour choper les infos pour le modèle Fama-French : https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
#Pour lancer l'application, tapez dans le terminal : /usr/local/bin/python3 -m streamlit run "/Users/tommylouhichi/Python/Fama-French/FF6.py"
#Attention à bien copier le chemin d'accès selon l'utilisateur sur cette partie "/Users/tommylouhichi/Python/Fama-French/FF6.py"
#Attention aussi sur cette partie-là si c'est un mac on laisse le 3 sinon on l'enlève pour les autres systèmes d'exploitation : /usr/local/bin/python3


#On demande à l'utilisateur de fournir le chemin du fichier CSV et on esquive les 4 premières lignes qui contiennent des infos inutiles pour nous
#On demande à l'utilisateur de fournir le chemin du fichier CSV des rendements du portefeuille et les dates de début et de fin de l'analyse
#Création d'une interface Streamlit pour afficher les résultats de la régression
st.title("Régression linéaire Fama-French 6 facteurs")
chemin_fichier = st.file_uploader("Entrez le fichier CSV de Fama-French 5 facteurs : ", type='csv')
st.info("À la prochaine étape il va falloir renseigner les rendements du portefeuille, la forme du fichier doit être la suivante : une 1ère colonne avec les dates au format YYYY-MM-DD (sur Excel mettre les données de la colonne Date en 'Texte') et une colonne avec les rendements du portefeuille en décimal (pas de 5% mais plutôt 0,05). Attention aussi à bien être en raccord avec les dates récentes de Fama-French 5 bien avoir comme titre 'Rendement du portefeuille' pour le titre de la colonne")
rendements_portefeuille = st.file_uploader("Entrez le fichier CSV des rendements du portefeuille : ", type='csv')
st.info("Attention regarder la date la plus ancienne du CSV de momentum et ne surtout pas mettre une date antérieur à cette date sinon l'analyse sera biaisée")
chemin_fichier_momentum = st.file_uploader("Entrez le fichier CSV de Fama-French avec le facteur momentum : ", type='csv')
date_debut = st.text_input("Entrez la date de début de l'analyse (format YYYY-MM-DD) : ")
date_fin = st.text_input("Entrez la date de fin de l'analyse (format YYYY-MM-DD) : ")

if chemin_fichier and rendements_portefeuille and chemin_fichier_momentum and date_debut and date_fin:
    
    facteurs = pd.read_csv(chemin_fichier, skiprows=4)
    facteurs_momentum = pd.read_csv(chemin_fichier_momentum, skiprows=3)

    #On donne un nom à la première colonne d'en tête vide qui contient les dates
    facteurs.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    facteurs_momentum.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)

    #On convertit la colonne date en texte, et on ne garde queles textes qui font exactement 6 caractères (ex: "196307") les lignes comme "1963" (4 caractères) ou les textes bizarres seront supprimés
    facteurs['Date'] = facteurs['Date'].astype(str).str.strip()
    facteurs_momentum['Date'] = facteurs_momentum['Date'].astype(str).str.strip()
    facteurs = facteurs[facteurs['Date'].str.len() == 6]
    facteurs_momentum = facteurs_momentum[facteurs_momentum['Date'].str.len() == 6]

    #Transformation en date 1963-01-01
    facteurs['Date'] = pd.to_datetime(facteurs['Date'], format='%Y%m')
    facteurs_momentum['Date'] = pd.to_datetime(facteurs_momentum['Date'], format='%Y%m')
    facteurs.set_index('Date', inplace=True)
    facteurs_momentum.set_index('Date', inplace=True)

    #Transformation en nombres
    facteurs = facteurs.astype(float)
    facteurs_momentum = facteurs_momentum.astype(float)

    #On divise tout le tableau par 100 pour avoir des 0,01 au lieu de 1
    facteurs = facteurs / 100
    facteurs_momentum = facteurs_momentum / 100

    #On applique les dates de début et de fin pour les 2 fichiers
    nouveau_tableau_rendements = pd.read_csv(rendements_portefeuille, parse_dates=True, index_col=0, sep=';', decimal=',')
    nouveau_tableau_rendements = nouveau_tableau_rendements.loc[date_debut:date_fin]
    nouveau_tableau_FF5 = facteurs.loc[date_debut:date_fin]
    nouveau_tableau_FF6 = facteurs_momentum.loc[date_debut:date_fin]

    #On fusionne les 2 tableaux pour n'avoir que les lignes avec des dates communes
    tableau_final = pd.concat([nouveau_tableau_rendements, nouveau_tableau_FF5, nouveau_tableau_FF6], axis=1)
    tableau_final['Excès de rendement'] = tableau_final['Rendement du portefeuille'] - tableau_final['RF']

    #Régression linéaire
    x = pd.concat([tableau_final['Mkt-RF'], tableau_final['SMB'], tableau_final['HML'], tableau_final['RMW'], tableau_final['CMA'], tableau_final['WML']], axis=1, ignore_index=True)
    x.columns = ("Prime de marché", "SMB", "HML", "RMW", "CMA", "WML")
    x = sm.add_constant(x)
    y = tableau_final['Excès de rendement']
    donnees_finales = pd.concat([y, x], axis=1).dropna()
    y_aligne = donnees_finales.iloc[:, 0]
    x_aligne = donnees_finales.iloc[:, 1:]
    modele = sm.OLS(y_aligne, x_aligne)
    resultats = modele.fit()

    alpha = resultats.params['const']
    beta_MARKET = resultats.params['Prime de marché']
    beta_SMB = resultats.params['SMB']
    beta_HML = resultats.params['HML']
    beta_RMW = resultats.params['RMW']
    beta_CMA = resultats.params['CMA']
    beta_WML = resultats.params['WML']

    p_value_alpha = resultats.pvalues['const']
    p_value_MARKET = resultats.pvalues['Prime de marché']
    p_value_SMB = resultats.pvalues['SMB']
    p_value_HML = resultats.pvalues['HML']
    p_value_RMW = resultats.pvalues['RMW']
    p_value_CMA = resultats.pvalues['CMA']
    p_value_WML = resultats.pvalues['WML']
    r_carre = resultats.rsquared_adj
    f_statistic = resultats.fvalue
    f_p_value = resultats.f_pvalue

    st.metric(label="Alpha : ", value=f"{alpha:.4f} & p-value : {p_value_alpha:.4f}") 
    st.metric(label="Prime de marché : ", value=f"{beta_MARKET:.4f} & p-value : {p_value_MARKET:.4f}")
    st.metric(label="Small Minus Big : ", value=f"{beta_SMB:.4f} & p-value : {p_value_SMB:.4f}")
    st.metric(label="High Minus Low : ", value=f"{beta_HML:.4f} & p-value : {p_value_HML:.4f}")
    st.metric(label="Robust Minus Weak : ", value=f"{beta_RMW:.4f} & p-value : {p_value_RMW:.4f}")
    st.metric(label="Conservative Minus Aggressive : ", value=f"{beta_CMA:.4f} & p-value : {p_value_CMA:.4f}")
    st.metric(label="Winning Minus Losers : ", value=f"{beta_WML:.4f} & p-value : {p_value_WML:.4f}")
    st.metric(label="R² ajusté : ", value=f"{r_carre:.4f}")
    st.metric(label="F-statistic : ", value=f"{f_statistic:.4f} & p-value : {f_p_value:.4f}")


    st.divider()

    st.write("### 💡 Aide à l'interprétation")

    with st.expander("Alpha"):
        st.write("""
    L'Alpha représente la performance du gérant qui n'est pas expliquée par les 6 facteurs de risque :
    - Un Alpha positif indique une surperformance par rapport au marché, tandis qu'un Alpha négatif indique une sous-performance
    """)

    with st.expander("Facteurs de risque (Bétas)"):
        st.write("""
    Prime de marché (Béta de marché MEDAF) :
    - Un coefficient de 1 signifie que le portefeuille suit le marché
    - Plus de 1 : le portefeuille est agressif (amplifie les mouvements)
    - Moins de 1 : il est défensif

                 
    Small Minus Big (SMB), c'est le facteur de taille :
    - Positif : Le gérant privilégie les Small Caps (plus de risque)
    - Négatif : Le gérant mise sur les Large Caps

                 
    High Minus Low (HML), c'est le facteur de style (Value vs Growth) :
    - Positif : Style Value. On achète des entreprises dont le prix est bas par rapport à leur valeur comptable (actions décotées)
    - Négatif : Style Growth. On mise sur des entreprises à forte croissance (souvent plus chères, comme la tech)

                 
    Robust Minus Weak (RMW), c'est le facteur de rentabilité :
    - Positif : Le portefeuille est exposé à des entreprises ayant des marges bénéficiaires solides et une haute qualité opérationnelle
    - Négatif : Exposition à des entreprises dont les profits sont plus fragiles ou spéculatifs

                 
    Conservative Minus Aggressive (CMA), c'est le facteur d'investissement :
    - Positif : Le gérant choisit des entreprises qui investissent de manière prudente et ciblée
    - Négatif : Exposition à des entreprises qui investissent massivement pour croître rapidement, ce qui peut être risqué sur le long terme
                 
    
    Winning Minus Losers (WML), c'est le facteur momentum :
    - Positif : Le portefeuille est exposé à des entreprises qui ont eu de bonnes performances récemment, ce qui peut indiquer une tendance à la hausse
    - Négatif : Exposition à des entreprises qui ont eu de mauvaises performances récemment, ce qui peut indiquer une tendance à la baisse
        """)

    with st.expander("P-value"):
        st.write("""
    La p-value permet de valider si un résultat est fiable ou s'il est dû au hasard :
    - Inférieure à 0.05 : Le résultat est statistiquement fiable
    - Supérieure à 0.05 : Le résultat n'est pas jugé significatif
    """)

    with st.expander("R² Ajusté"):
        st.write("""
    Le R² Ajusté indique la capacité du modèle Fama-French à expliquer les variations de votre portefeuille :
    - Proche de 1 : Le portefeuille suit fidèlement les facteurs de risque du marché
    - Proche de 0 : Le gérant prend des paris très spécifiques que le modèle ne capte pas
    """)

    with st.expander("F-statistic"):
        st.write("""
    La F-statistic répond à une question simple : Est-ce que ce modèle est plus utile qu'une simple moyenne ?
    Le concept : Le test compare votre modèle (avec les 6 facteurs) à un modèle vide (qui dirait juste que le rendement est égal à l'Alpha moyen). 
    Ordres de grandeur pour interpréter la valeur F :
    - Proche de 1 : le modèle n'est pas meilleur que le hasard. Le bruit domine le signal
    - Autour de 4 : le signal commence à être statistiquement significatif
    - Au-dessus de 10 : le modèle est considéré comme solide
    - Au-dessus de 50 : le modèle est très puissant (le portefeuille est très dépendant des facteurs choisis)

    En résumé, plus ce chiffre est élevé, plus vous pouvez avoir confiance dans le fait que vos facteurs expliquent réellement la performance du portefeuille.
    """)

else:
    st.info("Veuillez entrez tous les champs pour pouvoir lancer l'analyse.")