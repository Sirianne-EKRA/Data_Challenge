import requests
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# EXTRACTION DES DONNEES
url = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/283164601"
response = requests.get(url)
raw_data = response.json()

# Extraire la partie 'data'
df = pd.DataFrame(raw_data["data"])

# TRAITEMENT DES DONNEES

# Renommer les colonnes si nécessaire
df.rename(columns={
    'T. int.': 'T_int',
    'PM2.5': 'PM25'
}, inplace=True)

# Convertir les timestamps en format datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

# STOCKAGE DES DONNEES 
try:
    # Connexion à MongoDB
    client = MongoClient("mongodb://Admin:Mongo_MDP123456789@localhost:27018/admin?authSource=admin")
    db = client['test_Data354']
    collection = db['Stat1']
    
    # Récupérer le dernier document inséré pour obtenir le dernier timestamp
    last_doc = collection.find_one(sort=[("timestamp", -1)])  # Trier par timestamp décroissant
    last_timestamp = last_doc['timestamp'] if last_doc else datetime(1970, 1, 1)  # Valeur par défaut si aucun document

    # Filtrer les données pour ne conserver que celles avec un timestamp plus récent
    new_data = df[df['timestamp'] > last_timestamp]

    if not new_data.empty:
        # Insertion des données
        data_to_insert = new_data.to_dict('records')
        collection.insert_many(data_to_insert)
        print(f"{len(data_to_insert)} nouvelles données insérées avec succès dans MongoDB.")
    else:
        print("Aucune nouvelle donnée à insérer.")

except Exception as e:
    print("Erreur lors de la connexion ou insertion dans MongoDB :", e)
