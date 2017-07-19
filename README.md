# bus_track_compute
Calcul un tracé de parcours à partir des infos disponibles dans l'api navitia :
* récupère les arrêts desservis, dans l'ordre (à l'aide d'une grille horaire)
* calcule un itinéraire en voiture entre chaque couple d'arrêt
* renvoie un geojson, contenant les différentes étapes concaténées


## paramétrage
* dupliquer le répertoire auth_params_template, et le renomme en auth_params
* dans le fichier `__init__.py`, renseigner les informations d'authentification navitia
* tester
  * lancer `jupyter notebook` et lancer le notebook `exemple.ipynb`
  * renseigner un identifiant de parcours dans le paramètre `route_id`, et tester
