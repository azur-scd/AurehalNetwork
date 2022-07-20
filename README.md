# AurehalNetwork

![forthebadge](/assets/forthebadge.svg)

Application de visualisation des arborescences de structures dans Aurehal.

Démo : [https://azur-scd.com/apps/aurehal-network](https://azur-scd.com/apps/aurehal-network)

![aurehal-network](/assets/screenshot_uca.png)

Sur la base du docid d'une structure dans Aurehal, l'application remonte toutes les structures parentes ou récupère récursivement toutes les structures enfants de la structure courante et affiche la hiérarchie complète sous forme de graphe.

Le réseau des structures ainsi formé est ensuite configurable (couleur et taille des noeuds, filtres, disposition du graphe...) afin, par exemple, d'avoir une vue synthétique de la qualité de son référentiel de structures.

## Exemples de requêtes sur l'API HAL

### Obtenir les structures parentes (champ parentDocid_i) à partir du docid 1409

```
https://api.archives-ouvertes.fr/ref/structure/?wt=json&q=docid:409&fl=parentDocid_i

```
### Obtenir les structures enfants du docid 1039632

```
https://api.archives-ouvertes.fr/ref/structure/?wt=json&rows=1000&q=parentDocid_i:1039632&fl=docid,acronym_s,label_s,valid_s,type_s,address_s,parentDocid_i,url_s

```

### Obtenir le nombre de documents associés au docid 1039632

```
https://api.archives-ouvertes.fr/search/?wt=json&q=authStructId_i:1039632&rows=1

````

*Attention, dans le cas d'une requête initiale entraînant beaucoup de récursion, la récupération de tous les docid peut prendre qqs secondes*

## Dev

### Installation avec Docker

1. Avec l'image pré-buildée

Une image de ce repo est disponible sur le registre public Docker ici : [https://hub.docker.com/repository/docker/azurscd/aurehal-network](https://hub.docker.com/repository/docker/azurscd/aurehal-network)

Pour l'installer et lancer le container : 

```
docker run --name YOUR_CONTAINER_NAME -d -p 8050:8050 azurscd/aurehal-network:latest

```

2. Builder votre propre image

Vous pouvez également builder votre propre image avec le Dockerfile à la racine du repo.

```
docker build -t YOUR_IMAGE_NAME:TAG .
docker run --name YOUR_CONTAINER_NAME -d -p 8050:8050 YOUR_IMAGE_NAME:TAG
```
Lancer http://localhost:8050/aurehal-network/

## Installation avec Python Dash

```
git clone https://github.com/azur-scd/AurehalNetwork.git
```

### Créer un environnement virtuel et installer les dépendances dans ce virtualenv

```
python -m venv YOUR_VENV

# Windows
cd YOUR_VENV/Scripts & activate
# Linux
source VENV_NAME/bin/activate

pip install -r requirements.txt
```
### Lancer l'app

```
python app.py
```

Ouvrir http://localhost:8050/aurehal-network/



