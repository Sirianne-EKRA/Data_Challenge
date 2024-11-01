# README - Pipeline de gestion des données provenant de l'API airqino

Description du pipeline

La tâche à réaliser consiste  à construire un ETL pour :
- Extraire les données horaires depuis l'API de AirQuino
- Calculer le CO et le PM2.5 moyen par jour de chaque capteur
- Stocker les données résultantes dans une base de données (Cassandra ou mongoDB)
- Fournir un dashboard superset pour visualiser les données 
- Faire un modèle de mL qui fait du forecasting sur les 2 prochaines heures (Optionnel)


## PREREQUIS

1. Installer Docker
2. Installer Superset
    - git clone --depth=1  https://github.com/apache/superset.git
    - docker compose up -d

3. Cloner le repo github actuel et aller à la racine du projet.
4. Faire « docker compose up -d » pour installer les outils nécessaires à la mise en œuvre de l'ETL.


## DESCRIPTION DU TRAVAIL REALISE

La première partie du pipeline consistant en l'extraction, le traitement et stockage des données chaque heure a été implémenté de deux manières differentes. D'une part à l'aide de l'outil ETL Apache Nifi et d'autre part à l'aide d'un script python. 

### EXTRACTION - TRAITEMENT - CHARGEMENT DES DONNEES

#### Option 1: APACHE NIFI

Apache NiFi est un outil de gestion de flux de données qui permet de collecter, transformer et transférer des données entre systèmes de manière automatisée, en temps réel, avec une interface visuelle et des fonctionnalités de contrôle et de suivi. 
Cet ETL a été choisi en première option pour son facile déploiement, sa capacité à orchestrer des flux complexes sans code, et son support natif d'APIs, MongoDB et planification horaire, garantissant une extraction et un stockage efficace des données à intervalles réguliers.

##### Description de la solution avec Apache Nifi

Ce flux NiFi automatise le processus d’extraction, de traitement, et de chargement (ETL) des données depuis l'API vers une base de données MongoDB. À chaque exécution, le flux récupère toutes les données des jours disponibles via l’API, les filtre pour ne conserver que les enregistrements les plus récents par rapport aux données déjà stockées, effectue des transformations de renommage de certains champs, puis insère les nouvelles données dans MongoDB. L'ETL a été mis en place grâce à la configuration de plusieurs processeurs Nifi.


##### Etapes pour enclencher le processus

1. Accéder à l'interface visuelle de Nifi via l'URL https://localhost:8443/nifi/ 
2. Renseigner les identifiants USERNAME : Siri et PASSWORD : Nifi_MDP123456789#
3. Ayant accéder à l'interface de Nifi, faire clic droit et sélectionner l'option "Upload template" et charger le fichier Flux_Data354.xml présent dans le répertoire du repo github.
4. Sur la plus haute barre dans l'interface, faire un glisser déposer de l'élément "Template" (l'avant dernier élément sur la barre), sélectionner le template chargé précedemment et cliquer sur "ADD"
5. Faire clic droit dans l'interface et cliquer sur "Configure" pour activer la connexion à mongoDB: 
    - Cliquer sur l'icone de "Paramètres" = Configure à l'extrême droite de la ligne MongoDBControllerService;
    - Renseigner le mot de passe de Mongo "Mongo_MDP123456789" dans le champ "Password" et faire "Apply";
    - Cliquer sur le symbole "éclair" = "Enable" à la suite de "Configure" pour valider l'activation de la connexion;
    - Fermer la fenêtre.
6. Faire clic droit dans l'interface et cliquer sur "Start" pour déclencher tous les flux de données.

NB: Le premier processeur Nifi de chaque flux est exécuté chaque 60 minutes donc l'ETL est automatisé.

Ci-dessous un aperçu du flux Nifi implémenté:

<img width="893" alt="image" src="https://github.com/user-attachments/assets/1d111a0e-ed38-4626-ba6b-82b92d46496c">



#### Option 2: SCRIPT PYTHON

Le script python script_extract.py extrait les données depuis l'API, les traite et les insère dans la base de données MongoDB de manière conditionnelle. Le script suit les étapes suivantes :

1. Extraction des données : Une requête GET est envoyée à l'API pour récupérer les données sous format JSON, qui sont ensuite transformées en un DataFrame.
2. Traitement des données : Les données sont nettoyées et reformattées, y compris la conversion des timestamps en objets datetime et le renommage de certaines colonnes pour une meilleure lisibilité.
3. Insertion conditionnelle dans MongoDB : Le script se connecte à une base MongoDB et récupère le dernier document inséré pour obtenir le timestamp le plus récent. Il compare ensuite les timestamps pour ne conserver que les nouveaux enregistrements à insérer, en définissant une date par défaut pour les bases vides.
4. Gestion d'erreurs : En cas de problème de connexion ou d'insertion, le script affiche un message d'erreur spécifique.

Ce script permet ainsi de maintenir à jour la base de données MongoDB avec les données les plus récentes tout en évitant les doublons.

NB: Pour l'exécution automatique du script, il faut définir un cron sur le système de telle sorte à exécuter le code chaque une heure. Exemple:
- Faire crontab -e
- AJouter la ligne suivante :
0 * * * * /usr/bin/python3 /chemin/vers/script_extract.py >> /chemin/vers/logs/cron_log.txt 2>&1


### VISUALISATION DES DONNEES

La visualisation des données stockées dans MongoDB a été réalisée via Apache Superset, connecté à MongoDB en utilisant Trino comme couche intermédiaire. Trino sert de moteur SQL distribué permettant de requêter les données MongoDB et de les transformer en un format compréhensible pour Superset. Cette configuration permet de facilement créer des graphiques et de mettre en place des visualisations interactives sur les données extraites de l'API AirQino.

Dans Superset, trois principaux types de visualisations ont été configurés pour suivre l’évolution des polluants :

- Moyennes journalières de CO et PM2.5 par station 
- Comparaison des évolutions de CO et PM2.5 dans le temps
- Évolution temporelle des autres polluants (CO, NO2, O3, PM10, PM2.5)

Aperçu du dashboard réalisé ci-dessous:

![Capture d’écran 2024-11-01 170627](https://github.com/user-attachments/assets/6c743c18-de79-4627-becf-da60ad0f0dec)


L'export du dashboard se trouve dans le fichier dashboard_Air_Quality_export.zip
