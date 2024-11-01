import requests
import json
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

ids={"283164601":"station1", "283181971":"station2"}

for key, value in ids.items():


    # EXTRACTION DES DONNEES
    url = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/" + key

    response = requests.get(url)
    data = response.json()
    raw_data = response.json()
    # Extraire la partie 'data'
    df = pd.DataFrame(raw_data["data"])
    df['station']=value

    # TRAITEMENT DES DONNEES
    df.rename(columns={
        'timestamp':'horodatage',
        'T. int.': 'T_int',
        'PM2.5': 'PM25'
    }, inplace=True)
    df['horodatage'] = pd.to_datetime(df['horodatage'], format='%Y-%m-%d %H:%M:%S')

    # STOCKAGE DES DONNEES 
    try:
        # Connexion à MongoDB
        client = MongoClient("mongodb://Admin:Mongo_MDP123456789@localhost:27018/admin?authSource=admin")
        db = client['airquality']
        collection = db['station']
        
        # Récupérer le dernier document inséré pour obtenir le dernier horodatage
        last_doc = collection.find_one({"station": value}, sort=[("horodatage", -1)])
        last_timestamp = last_doc['horodatage'] if last_doc else datetime(1970, 1, 1)  
        # Filtrer les données pour ne conserver que celles avec un horodatage plus récent
        new_data = df[df['horodatage'] > last_timestamp]
        if not new_data.empty:
            # Insertion des données
            data_to_insert = new_data.to_dict('records')
            collection.insert_many(data_to_insert)
            print(f"{len(data_to_insert)} nouvelles données insérées avec succès dans MongoDB.")
        else:
            print("Aucune nouvelle donnée à insérer.")
    except Exception as e:
        print("Erreur lors de la connexion ou insertion dans MongoDB :", e)