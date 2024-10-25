# README - Pipeline de gestion des données provenant de l'API airqino

Description du pipeline

La tâche à réaliser consiste construire un ETL pour :
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

### Option 1: APACHE NIFI

Apache NiFi est un outil de gestion de flux de données qui permet de collecter, transformer et transférer des données entre systèmes de manière automatisée, en temps réel, avec une interface visuelle et des fonctionnalités de contrôle et de suivi. 
Cet ETL a été choisi en première option pour son facile déploiement, sa capacité à orchestrer des flux complexes sans code, et son support natif d'APIs, MongoDB et planification horaire, garantissant une extraction et un stockage efficace des données à intervalles réguliers.

Etapes pour enc

1. Accéder à l'interface visuelle de Nifi via l'URL https://localhost:8443/nifi/ 
2. Renseigner les identifiants USERNAME : Siri et PASSWORD : Nifi_MDP123456789#
3. Ayant accéder à l'interface de Nifi, faire clic droit et sélectionner l'option "Upload template" et charger le fichier final.xml présent dans le répertoire du repo github.
4. Sur la plus haute barre dans l'interface, faire un glisser déposer de l'élément "Template" (l'avant dernier élément sur la barre), sélectionner le template chargé précedemment et cliquer sur "ADD"
5. Faire clic droit dans l'interface et cliquer sur "Start" pour déclencher tous les flux de données.

NB: Les deux premiers processeurs Nifi de chaque flux sont exécutés chaque 60 minutes donc l'ETL est automatisé.


### Option 2: SCRIPT PYTHON


