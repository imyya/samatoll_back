"""
Machine Learning Models for Humidity Prediction in Senegal
Version finale avec sauvegarde du meilleur modèle
"""

# ==================== IMPORTS ====================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pickle
import joblib
import os

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

import xgboost as xgb

import warnings
warnings.filterwarnings('ignore')

print("✅ Toutes les bibliothèques importées avec succès!")

# ==================== LOADING DATA ====================
print("\n" + "="*50)
print("CHARGEMENT DES DONNÉES")
print("="*50)

df = pd.read_csv('meteo_departements_Senegal.csv')
print(f"✅ Données chargées: {df.shape[0]} lignes, {df.shape[1]} colonnes")

# ==================== DATA CLEANING ====================
print("\n" + "="*50)
print("NETTOYAGE DES DONNÉES")
print("="*50)

# Supprimer les doublons
df_clean = df.drop_duplicates().copy()
print(f"✅ Doublons supprimés. Données après nettoyage: {df_clean.shape[0]} lignes")

# Convertir la colonne date
df_clean['date'] = pd.to_datetime(df_clean['date'])

# Extraire des caractéristiques de la date
df_clean['mois'] = df_clean['date'].dt.month
df_clean['jour'] = df_clean['date'].dt.day
df_clean['heure'] = df_clean['date'].dt.hour

print(f"✅ Caractéristiques temporelles extraites")

# ==================== FEATURE PREPARATION ====================
print("\n" + "="*50)
print("PRÉPARATION DES CARACTÉRISTIQUES")
print("="*50)

# Encoder les catégories
le_region_dict = {val: idx for idx, val in enumerate(df_clean['region'].unique())}
le_departement_dict = {val: idx for idx, val in enumerate(df_clean['departement'].unique())}

# Encoder weather avec un ordre logique
weather_order = {
    'clear sky': 0,
    'few clouds': 1,
    'scattered clouds': 2,
    'broken clouds': 3,
    'overcast clouds': 4,
    'light rain': 5,
    'moderate rain': 6,
    'heavy rain': 7,
    'thunderstorm with rain': 8
}

def encode_weather(weather):
    return weather_order.get(weather, 4)

# Appliquer l'encodage
df_encoded = df_clean.copy()
df_encoded['region_code'] = df_encoded['region'].map(le_region_dict)
df_encoded['departement_code'] = df_encoded['departement'].map(le_departement_dict)
df_encoded['weather_code'] = df_encoded['weather'].apply(encode_weather)

# Sélectionner les features finales
feature_columns = [
    'region_code',
    'departement_code',
    'weather_code',
    'temperature',
    'wind_speed',
    'mois',
    'jour',
    'heure'
]

X = df_encoded[feature_columns]
y = df_encoded['humidity']

print(f"✅ Features sélectionnées: {len(feature_columns)}")

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n✅ Split train/test (80/20):")
print(f"   - Training: {X_train.shape[0]} échantillons")
print(f"   - Test: {X_test.shape[0]} échantillons")

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✅ Données standardisées")

# ==================== MODEL TRAINING ====================
print("\n" + "="*50)
print("ENTRAÎNEMENT DES MODÈLES")
print("="*50)

models = {
    'Linear Regression': LinearRegression(),
    'Ridge': Ridge(),
    'Lasso': Lasso(),
    'ElasticNet': ElasticNet(),
    'Random Forest': RandomForestRegressor(random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(random_state=42),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'XGBoost': xgb.XGBRegressor(random_state=42, n_jobs=-1)
}

results = []

for name, model in models.items():
    print(f"\n🔧 Entraînement: {name}...")
    
    if name in ['Linear Regression', 'Ridge', 'Lasso', 'ElasticNet']:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    results.append({
        'Model': name,
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'MSE': mse
    })
    
    print(f"   - RMSE: {rmse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}")

# ==================== RESULTS COMPARISON ====================
print("\n" + "="*50)
print("COMPARAISON DES MODÈLES")
print("="*50)

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('RMSE')
print("\n📊 Résultats par RMSE (du meilleur au pire):")
print(results_df.to_string(index=False))

# ==================== SELECT BEST MODEL ====================
print("\n" + "="*50)
print("SÉLECTION DU MEILLEUR MODÈLE")
print("="*50)

# Entraîner à nouveau le meilleur modèle sur toutes les données
best_model_name = results_df.iloc[0]['Model']
print(f"🏆 Meilleur modèle: {best_model_name}")

# Recréer le meilleur modèle
if best_model_name in ['Linear Regression', 'Ridge', 'Lasso', 'ElasticNet']:
    best_model = models[best_model_name]
    best_model.fit(X_train_scaled, y_train)
    use_scaler = True
else:
    best_model = models[best_model_name]
    best_model.fit(X_train, y_train)
    use_scaler = False

print(f"✅ Modèle réentraîné sur l'ensemble des données d'entraînement")

# Évaluation finale
if use_scaler:
    y_pred = best_model.predict(X_test_scaled)
else:
    y_pred = best_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"\n📊 Performance finale:")
print(f"   - RMSE: {rmse:.2f}")
print(f"   - MAE: {mae:.2f}")
print(f"   - R²: {r2:.4f}")

# Feature importance
if hasattr(best_model, 'feature_importances_'):
    print("\n📊 Importance des caractéristiques:")
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance_df.to_string(index=False))

# ==================== SAVE MODEL ====================
print("\n" + "="*50)
print("SAUVEGARDE DU MODÈLE")
print("="*50)

# Créer le dossier models s'il n'existe pas
os.makedirs('models', exist_ok=True)

# Sauvegarder le modèle
model_filename = 'models/best_humidity_model.pkl'
joblib.dump(best_model, model_filename)
print(f"✅ Modèle sauvegardé: {model_filename}")

# Sauvegarder le scaler
scaler_filename = 'models/scaler.pkl'
joblib.dump(scaler, scaler_filename)
print(f"✅ Scaler sauvegardé: {scaler_filename}")

# Sauvegarder les encoders
encoders = {
    'region_dict': le_region_dict,
    'departement_dict': le_departement_dict,
    'weather_order': weather_order
}
encoders_filename = 'models/encoders.pkl'
joblib.dump(encoders, encoders_filename)
print(f"✅ Encoders sauvegardés: {encoders_filename}")

# Sauvegarder les feature columns
feature_columns_filename = 'models/feature_columns.pkl'
joblib.dump(feature_columns, feature_columns_filename)
print(f"✅ Feature columns sauvegardées: {feature_columns_filename}")

# Sauvegarder les métadonnées du modèle
model_metadata = {
    'model_name': best_model_name,
    'use_scaler': use_scaler,
    'feature_columns': feature_columns,
    'train_rmse': rmse,
    'train_mae': mae,
    'train_r2': r2,
    'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'n_samples_train': len(X_train),
    'n_samples_test': len(X_test)
}
metadata_filename = 'models/model_metadata.pkl'
joblib.dump(model_metadata, metadata_filename)
print(f"✅ Métadonnées sauvegardées: {metadata_filename}")

# Créer un fichier de sauvegarde avec toutes les informations
summary_filename = 'models/model_summary.txt'
with open(summary_filename, 'w', encoding='utf-8') as f:
    f.write("="*50 + "\n")
    f.write("RÉSUMÉ DU MEILLEUR MODÈLE\n")
    f.write("="*50 + "\n\n")
    f.write(f"📅 Date d'entraînement: {model_metadata['training_date']}\n")
    f.write(f"🏆 Modèle: {best_model_name}\n")
    f.write(f"📊 Performance:\n")
    f.write(f"   - RMSE: {rmse:.2f}\n")
    f.write(f"   - MAE: {mae:.2f}\n")
    f.write(f"   - R²: {r2:.4f}\n\n")
    f.write(f"📈 Données:\n")
    f.write(f"   - Échantillons d'entraînement: {model_metadata['n_samples_train']}\n")
    f.write(f"   - Échantillons de test: {model_metadata['n_samples_test']}\n\n")
    f.write(f"🔧 Utilise le scaler: {use_scaler}\n\n")
    f.write(f"📋 Caractéristiques:\n")
    for feat in feature_columns:
        f.write(f"   - {feat}\n")
    f.write("\n" + "="*50 + "\n")
    f.write("Comparaison avec autres modèles:\n")
    f.write("="*50 + "\n")
    f.write(results_df.to_string())

print(f"✅ Résumé sauvegardé: {summary_filename}")

# ==================== VISUALIZATIONS ====================
print("\n" + "="*50)
print("GÉNÉRATION DES VISUALISATIONS")
print("="*50)

# Créer le dossier images s'il n'existe pas
os.makedirs('images', exist_ok=True)

# 1. Comparaison des modèles
plt.figure(figsize=(10, 6))
results_df_top = results_df.head(5)
plt.barh(results_df_top['Model'], results_df_top['RMSE'])
plt.xlabel('RMSE (Root Mean Squared Error)')
plt.title('Comparaison des 5 meilleurs modèles')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('images/model_comparison.png', dpi=150, bbox_inches='tight')
print("✅ Graphique de comparaison sauvé: images/model_comparison.png")

# 2. Prédictions vs Réalité
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Valeurs réelles')
plt.ylabel('Prédictions')
plt.title(f'Prédictions vs Réalité - {best_model_name}')
plt.tight_layout()
plt.savefig('images/predictions_vs_reality.png', dpi=150, bbox_inches='tight')
print("✅ Graphique prédictions/réalité sauvé: images/predictions_vs_reality.png")

# 3. Feature importance
if hasattr(best_model, 'feature_importances_'):
    plt.figure(figsize=(10, 6))
    importance_df.plot(x='feature', y='importance', kind='barh', legend=False)
    plt.xlabel('Importance')
    plt.title(f'Importance des caractéristiques - {best_model_name}')
    plt.tight_layout()
    plt.savefig('images/feature_importance.png', dpi=150, bbox_inches='tight')
    print("✅ Graphique d'importance sauvé: images/feature_importance.png")

print("\n" + "="*50)
print("✅ PROCESSUS TERMINÉ AVEC SUCCÈS!")
print("="*50)
print(f"\n🏆 Fichiers créés dans le dossier 'models/':")
print(f"   - best_humidity_model.pkl (modèle)")
print(f"   - scaler.pkl (standardisation)")
print(f"   - encoders.pkl (encodages)")
print(f"   - feature_columns.pkl (colonnes)")
print(f"   - model_metadata.pkl (métadonnées)")
print(f"   - model_summary.txt (résumé lisible)")
print(f"\n📊 Graphiques dans 'images/':")
print(f"   - model_comparison.png")
print(f"   - predictions_vs_reality.png")
print(f"   - feature_importance.png")

