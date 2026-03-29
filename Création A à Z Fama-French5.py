import pandas as pd
import yfinance as yf
import numpy as np
import statsmodels.api as sm

#sélection des tickers du CAC 40

tickers_cac_40 = ['AC.PA', 'AI.PA', 'AIR.PA', 'MT.AS', 'CS.PA', 'BNP.PA', 'EN.PA', 'CAP.PA', 
    'CA.PA', 'ACA.PA', 'BN.PA', 'DSY.PA', 'EDEN.PA', 'ENGI.PA', 'EL.PA', 'ERF.PA', 
    'RMS.PA', 'KER.PA', 'LR.PA', 'OR.PA', 'MC.PA', 'ML.PA', 'ORA.PA', 'RI.PA', 
    'PUB.PA', 'RNO.PA', 'SAF.PA', 'SGO.PA', 'SAN.PA', 'SU.PA', 'GLE.PA', 'STLAP.PA', 
    'STMPA.PA', 'TEP.PA', 'HO.PA', 'TTE.PA', 'URW.PA', 'VIE.PA', 'DG.PA', 'WLN.PA']

#choix des donnéees en fonction de la date et mensuel

donnees = yf.download(tickers_cac_40, start = "2020-07-01", end = "2024-12-31", interval = "1mo")

#ajustement des prix afin de tenir compte des dividendes

prix_ajustes = donnees['Close']

#calcul du rendement mensuel avec logarithme de M/M-1

rendements_mensuels = np.log(prix_ajustes / prix_ajustes.shift(1))

#le modèle Fama-French classe les entreprises uniquement en juin et fige cette classification jusqu'au mois de juin prochain si changement il y a

prix_juin = prix_ajustes[prix_ajustes.index.month == 6]

#calcul de la capitalisation boursière sur la base des actions en circulation aujourd'hui - en vrai on pourrait recréer un fichier csv avec la data

actions_en_circulation = {}

for i in tickers_cac_40:
    infos = yf.Ticker(i).info
    actions_en_circulation[i] = infos.get('sharesOutstanding', np.nan)

transformation_en_serie = pd.Series(actions_en_circulation)

capitalisation_boursiere = transformation_en_serie * prix_juin

#On calcule la médiane pour chaque année (sur l'axe horizontal des entreprises)

median_annuelle = capitalisation_boursiere.median(axis=1)

#gt() veut dire "greater than" (strictement supérieur)

big_vs_small_caps = capitalisation_boursiere.gt(median_annuelle, axis=0)

#ajout des données fictives de valeurs comptables créées sur excel et transformé en CSV et séparées par un point virgule 

valeur_comptable_annuel = pd.read_csv('/Users/tommylouhichi/Desktop/Portefeuille/CAC 40 valeurs comptables.csv', index_col=0, parse_dates=True, sep=";")

#on ajoute +1 aux valeur comptables car il y a un déclage d'un an étant donné que pour la cap boursière de 2021 on prend la VC 2020

valeur_comptable_annuel.index = valeur_comptable_annuel.index + pd.DateOffset(years=1)

capitalisation_boursiere = capitalisation_boursiere.resample('MS').ffill()

valeur_comptable_annuel = valeur_comptable_annuel.resample('MS').ffill()

book_to_market = valeur_comptable_annuel / capitalisation_boursiere

seuil_30 = book_to_market.quantile(0.3, axis=1)

seuil_70 = book_to_market.quantile(0.7, axis=1)

growth = book_to_market.lt(seuil_30, axis=0)

neutral = (book_to_market.ge(seuil_30, axis=0)) & (book_to_market.le(seuil_70, axis=0))

value = book_to_market.gt(seuil_70, axis=0)

#classficiation des 6 PTF

small_caps_growth = ~big_vs_small_caps & growth

small_caps_neutral = ~big_vs_small_caps & neutral

small_caps_value = ~big_vs_small_caps & value

big_caps_growth = big_vs_small_caps & growth

big_caps_neutral = big_vs_small_caps & neutral

big_caps_value = big_vs_small_caps & value

#calcul des rendements pondérés de chaque portefeuille

p_small_caps_growth = capitalisation_boursiere[small_caps_growth].div(capitalisation_boursiere[small_caps_growth].sum(axis=1), axis=0)

rp_small_caps_growth = rendements_mensuels[small_caps_growth] * p_small_caps_growth

return_small_caps_growth = rp_small_caps_growth.sum(axis=1)

p_small_caps_neutral = capitalisation_boursiere[small_caps_neutral].div(capitalisation_boursiere[small_caps_neutral].sum(axis=1), axis=0)

rp_small_caps_neutral = rendements_mensuels[small_caps_neutral] * p_small_caps_neutral

return_small_caps_neutral = rp_small_caps_neutral.sum(axis=1)

p_small_caps_value = capitalisation_boursiere[small_caps_value].div(capitalisation_boursiere[small_caps_value].sum(axis=1), axis=0)

rp_small_caps_value = rendements_mensuels[small_caps_value] * p_small_caps_value

return_small_caps_value = rp_small_caps_value.sum(axis=1)

p_big_caps_growth = capitalisation_boursiere[big_caps_growth].div(capitalisation_boursiere[big_caps_growth].sum(axis=1), axis=0)

rp_big_caps_growth = rendements_mensuels[big_caps_growth] * p_big_caps_growth

return_big_caps_growth = rp_big_caps_growth.sum(axis=1)

p_big_caps_neutral = capitalisation_boursiere[big_caps_neutral].div(capitalisation_boursiere[big_caps_neutral].sum(axis=1), axis=0)

rp_big_caps_neutral = rendements_mensuels[big_caps_neutral] * p_big_caps_neutral

return_big_caps_neutral = rp_big_caps_neutral.sum(axis=1)

p_big_caps_value = capitalisation_boursiere[big_caps_value].div(capitalisation_boursiere[big_caps_value].sum(axis=1), axis=0)

rp_big_caps_value = rendements_mensuels[big_caps_value] * p_big_caps_value

return_big_caps_value = rp_big_caps_value.sum(axis=1)

#calcul des facteurs SMB et HML

small_minus_big = (return_small_caps_growth + return_small_caps_neutral + return_small_caps_value)/3 - (return_big_caps_growth + return_big_caps_neutral + return_big_caps_value)/3

high_minus_low = (return_small_caps_value + return_big_caps_value)/2 - (return_small_caps_growth + return_big_caps_growth)/2

#récupération de la rémunération du CAC 40 comme indice de référence

CAC_40 = yf.download('^FCHI', start = "2020-07-01", end = "2024-12-31", interval="1mo")

CAC_40 = CAC_40['Close'].squeeze()

CAC_40 = np.log(CAC_40/CAC_40.shift(1))

#récupération du RFR

RFR = yf.download('^IRX', start="2020-07-01", end="2024-12-31", interval="1mo")

RFR = RFR['Close'].squeeze()

RFR = np.log(1 + (RFR/100)) / 12

#calcul de la prime de risque de marché

prime_risque_marche = CAC_40-RFR

#calcul des excès de rendements des portefeuilles

excess_return_small_caps_growth = return_small_caps_growth - RFR

excess_return_small_caps_neutral = return_small_caps_neutral - RFR

excess_return_small_caps_value = return_small_caps_value - RFR

excess_return_big_caps_growth = return_big_caps_growth - RFR

excess_return_big_caps_neutral = return_big_caps_neutral - RFR

excess_return_big_caps_value = return_big_caps_value - RFR

#nous venons de finir juste au-dessus le modèle FF3 passons aux 2 parmaètres supplémentaires avec FF5

resultat_exploitation = pd.read_csv('/Users/tommylouhichi/Desktop/Portefeuille/CAC 40 REX.csv', index_col=0, parse_dates=True, sep=";")

resultat_exploitation.index = resultat_exploitation.index + pd.DateOffset(years=1)

resultat_exploitation = resultat_exploitation.resample('MS').ffill()

capitaux_propres = pd.read_csv('/Users/tommylouhichi/Desktop/Portefeuille/CAC 40 capitaux propres.csv', index_col=0, parse_dates=True, sep=";")

capitaux_propres.index = capitaux_propres.index + pd.DateOffset(years=1)

capitaux_propres = capitaux_propres.resample('MS').ffill()

rentabilite = resultat_exploitation.div(capitaux_propres, axis=0)

investissement = pd.read_csv('/Users/tommylouhichi/Desktop/Portefeuille/CAC 40 investissements.csv', index_col=0, parse_dates=True, sep=";")

investissement = (investissement / investissement.shift(1)) - 1 

investissement.index = investissement.index + pd.DateOffset(years=1)

investissement = investissement.resample('MS').ffill()

seuil_30_r = rentabilite.quantile(0.3, axis=1)

seuil_70_r = rentabilite.quantile(0.7, axis=1)

weak_r = rentabilite.lt(seuil_30_r, axis=0)

neutral_r = rentabilite.ge(seuil_30_r, axis=1) & rentabilite.le(seuil_70_r, axis=0)

robust_r = rentabilite.gt(seuil_70_r, axis=0)

small_caps_weak = ~big_vs_small_caps & weak_r

small_caps_neutral_r = ~big_vs_small_caps & neutral_r

small_caps_robust = ~big_vs_small_caps & robust_r

large_caps_weak = big_vs_small_caps & weak_r

large_caps_neutral_r = big_vs_small_caps & neutral_r

large_caps_robust = big_vs_small_caps & robust_r

seuil_30_inv = investissement.quantile(0.3, axis=1)

seuil_70_inv = investissement.quantile(0.7, axis=1)

conservatrice_inv = investissement.lt(seuil_30_inv, axis=0)

neutral_inv = investissement.ge(seuil_30_inv, axis=1) & investissement.le(seuil_70_inv, axis=0)

agressive_inv = investissement.gt(seuil_70_inv, axis=0)

small_caps_conservatrice = ~big_vs_small_caps & conservatrice_inv

small_caps_neutral_inv = ~big_vs_small_caps & neutral_inv

small_caps_agressive = ~big_vs_small_caps & agressive_inv

large_caps_conservatrice = big_vs_small_caps & conservatrice_inv

large_caps_neutral_inv = big_vs_small_caps & neutral_inv

large_caps_agressive = big_vs_small_caps & agressive_inv

p_small_caps_weak = capitalisation_boursiere[small_caps_weak].div(capitalisation_boursiere[small_caps_weak].sum(axis=1), axis=0)

rp_small_caps_weak = rendements_mensuels[small_caps_weak] * p_small_caps_weak

return_small_caps_weak = rp_small_caps_weak.sum(axis=1)

p_small_caps_neutral_r = capitalisation_boursiere[small_caps_neutral_r].div(capitalisation_boursiere[small_caps_neutral_r].sum(axis=1), axis=0)

rp_small_caps_neutral_r = rendements_mensuels[small_caps_neutral_r] * p_small_caps_neutral_r

return_small_caps_neutral_r = rp_small_caps_neutral_r.sum(axis=1)

p_small_caps_robust = capitalisation_boursiere[small_caps_robust].div(capitalisation_boursiere[small_caps_robust].sum(axis=1), axis=0)

rp_small_caps_robust = rendements_mensuels[small_caps_robust] * p_small_caps_robust

return_small_caps_robust = rp_small_caps_robust.sum(axis=1)

p_large_caps_weak = capitalisation_boursiere[large_caps_weak].div(capitalisation_boursiere[large_caps_weak].sum(axis=1), axis=0)

rp_large_caps_weak = rendements_mensuels[large_caps_weak] * p_large_caps_weak

return_large_caps_weak = rp_large_caps_weak.sum(axis=1)

p_large_caps_neutral_r = capitalisation_boursiere[large_caps_neutral_r].div(capitalisation_boursiere[large_caps_neutral_r].sum(axis=1), axis=0)

rp_large_caps_neutral_r = rendements_mensuels[large_caps_neutral_r] * p_large_caps_neutral_r

return_large_caps_neutral_r = rp_large_caps_neutral_r.sum(axis=1)

p_large_caps_robust = capitalisation_boursiere[large_caps_robust].div(capitalisation_boursiere[large_caps_robust].sum(axis=1), axis=0)

rp_large_caps_robust = rendements_mensuels[large_caps_robust] * p_large_caps_robust

return_large_caps_robust = rp_large_caps_robust.sum(axis=1)

p_small_caps_conservatrice = capitalisation_boursiere[small_caps_conservatrice].div(capitalisation_boursiere[small_caps_conservatrice].sum(axis=1), axis=0)

rp_small_caps_conservatrice = rendements_mensuels[small_caps_conservatrice] * p_small_caps_conservatrice

return_small_caps_conservatrice = rp_small_caps_conservatrice.sum(axis=1)

p_small_caps_neutral_inv = capitalisation_boursiere[small_caps_neutral_inv].div(capitalisation_boursiere[small_caps_neutral_inv].sum(axis=1), axis=0)

rp_small_caps_neutral_inv = rendements_mensuels[small_caps_neutral_inv] * p_small_caps_neutral_inv

return_small_caps_neutral_inv = rp_small_caps_neutral_inv.sum(axis=1)

p_small_caps_agressive = capitalisation_boursiere[small_caps_agressive].div(capitalisation_boursiere[small_caps_agressive].sum(axis=1), axis=0)

rp_small_caps_agressive = rendements_mensuels[small_caps_agressive] * p_small_caps_agressive

return_small_caps_agressive = rp_small_caps_agressive.sum(axis=1)

p_large_caps_conservatrice = capitalisation_boursiere[large_caps_conservatrice].div(capitalisation_boursiere[large_caps_conservatrice].sum(axis=1), axis=0)

rp_large_caps_conservatrice = rendements_mensuels[large_caps_conservatrice] * p_large_caps_conservatrice

return_large_caps_conservatrice = rp_large_caps_conservatrice.sum(axis=1)

p_large_caps_neutral_inv = capitalisation_boursiere[large_caps_neutral_inv].div(capitalisation_boursiere[large_caps_neutral_inv].sum(axis=1), axis=0)

rp_large_caps_neutral_inv = rendements_mensuels[large_caps_neutral_inv] * p_large_caps_neutral_inv

return_large_caps_neutral_inv = rp_large_caps_neutral_inv.sum(axis=1)

p_large_caps_agressive = capitalisation_boursiere[large_caps_agressive].div(capitalisation_boursiere[large_caps_agressive].sum(axis=1), axis=0)

rp_large_caps_agressive = rendements_mensuels[large_caps_agressive] * p_large_caps_agressive

return_large_caps_agressive = rp_large_caps_agressive.sum(axis=1)

RMW = (return_large_caps_robust + return_small_caps_robust) - (return_small_caps_weak + return_large_caps_weak)

CMA = (return_large_caps_conservatrice + return_small_caps_conservatrice) - (return_small_caps_agressive + return_large_caps_agressive)

x = pd.concat([prime_risque_marche, small_minus_big, high_minus_low, RMW, CMA], axis=1)

x.columns = ("prime_marché", "SMB", "HML", "RMW", "CMA")

x = sm.add_constant(x)

y = excess_return_small_caps_growth

donnees_finales = pd.concat([y, x], axis=1).dropna()

y_aligne = donnees_finales.iloc[:, 0]

x_aligne = donnees_finales.iloc[:, 1:]

modele = sm.OLS(y_aligne, x_aligne)

resultats = modele.fit()

print(resultats.summary())