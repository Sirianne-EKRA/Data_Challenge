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
2. Clôner le repository github et se mettre à la racine du projet
3. Lancer les commandes suivantes pour télécharger les images des outils à utiliser : Apache Nifi, MongoDB et Superset.

    - docker pull mongo
    - docker pull apache/nifi:1.26.0
    - docker pull apache/superset
    - docker compose up -d

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

NB: Les deux premiers processeurs Nifi de chaque flux sont exécutés chaque 60 minutes donc l'ETL est automatisé.


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
