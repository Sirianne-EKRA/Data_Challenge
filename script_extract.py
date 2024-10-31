import requests 
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# EXTRACTION DES DONNÉES
url = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/283181971"
response = requests.get(url)
raw_data = response.json()

# Extraire la partie 'data'
df = pd.DataFrame(raw_data["data"])

# Renommer les colonnes si nécessaire
df.rename(columns={'timestamp': 'horodatage','T. int.': 'T_int', 'PM2.5': 'PM25'}, inplace=True)

# Convertir les horodatages en format datetime
df['horodatage'] = pd.to_datetime(df['horodatage'], format='%Y-%m-%d %H:%M:%S')
df['jour'] = df['horodatage'].dt.date  # Extraire uniquement la date pour le regroupement

# Connexion à MongoDB
client = MongoClient("mongodb://Admin:Mongo_MDP123456789@localhost:27018/admin?authSource=admin")
db = client['airquality']
collection = db['station2']

# Récupérer le dernier document inséré pour obtenir le dernier horodatage
last_doc = collection.find_one(sort=[("horodatage", -1)])
last_horodatage = last_doc['horodatage'] if last_doc else datetime(1970, 1, 1)

# Filtrer les données pour ne conserver que celles avec un horodatage plus récent
new_data = df[df['horodatage'] > last_horodatage]

if not new_data.empty:
    # Calcul des moyennes cumulées pour chaque ligne jusqu'à l'heure du horodatage actuel
    results = []
    for i, row in new_data.iterrows():
        # Filtrer les données du même jour jusqu'à l'heure du horodatage actuel
        day_data = new_data[(new_data['jour'] == row['jour']) & (new_data['horodatage'] <= row['horodatage'])]
        
        # Calculer les moyennes cumulées de CO et PM25
        CO_moy = day_data['CO'].mean()
        PM25_moy = day_data['PM25'].mean()
        
        # Ajouter les valeurs de moyennes calculées dans la ligne
        row_data = row.to_dict()
        row_data['CO_moy'] = CO_moy
        row_data['PM25_moy'] = PM25_moy
         # Convertir 'jour' en chaîne de caractères pour MongoDB
        row_data['jour'] = row_data['jour'].strftime('%Y-%m-%d')

        results.append(row_data)
    
    # Insérer les données dans MongoDB
    collection.insert_many(results)
    print(f"{len(results)} nouvelles données insérées avec succès dans MongoDB.")
else:
    print("Aucune nouvelle donnée à insérer.")
