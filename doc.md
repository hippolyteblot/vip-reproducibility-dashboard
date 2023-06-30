# Documentation

Le dashboard lié à l’étude de la reproductibilité du portail VIP est basé sur le framework Python **Dash** (Plotly). Il nécessite également une base de données MySQL ainsi qu’un accès à une instance du logiciel Girder (grâce à l’utilisation d’une clé)

# Architecture du dashboard

Le dashboard repose sur un modèle **[MVC](https://fr.wikipedia.org/wiki/Mod%C3%A8le-vue-contr%C3%B4leur)**. Voici une explication de sa structure :

- `assets` : contient les différentes ressources nécessaires (images, scripts, feuilles de styles…)
- `components` : composants complexes utilisés sur les pages de dashboard
- `models` : contient les fichiers proposant des fonction d’accès et de traitement des données
- `pages` : contient les contrôleurs faisant appel aux modèles et aux vues
- `tmp` : stocke les données téléchargées par le dashboard à la demande des utilisateurs
- `utils` : propose différentes fonctions et objets utilisés dans le code du dashboard (client pour la base de données, variables de configuration du serveur…)
- `views` : contient les vues de l’application, c’est à dire ce qui est envoyé au navigateur du client

## Spécificité du dossier assets

Ce dossier possède quelques spécificités liées au framework Dash.

Tous les fichiers de style et de script à la racine de ce dossier sont automatiquement chargés sur le dashboard. De plus, le fichier `favicon.ico` présent dans le dossier logos est automatiquement reconnu par Dash comme le logo de l’application.

## Composants

### Composant Login

Ce composant sert à adapter le contenu du dashboard en fonction du status de l’utilisateur. Si celui-ci est connecté, la barre de navigation sera différente et celui-ci pourra accéder à d’autre onglet. Ce système, géré par le composant `login`, repose sur l’objet `current_user` de la librairie [Flask-Login](https://flask-login.readthedocs.io/en/latest/). Grâce à lui, le dashboard identifie si l”utilisateur est connecté ainsi que son rôle (définis dans la table USERS de la base de données) et gère les accès ainsi que les composants à afficher.

### Composant Navbar

La barre de navigation de l’application s’adapte au status de l’utilisateur. Dans le cas ou celui-ci est connecté et possède un rôle administrateur, il pourra accéder à un onglet supplémentaire : **Add experiment**.

Pour gérer ce fonctionnement, elle fait appel au composant login qui lui fournira les éléments à afficher ou non (onglet ****************************Add Experiment****************************).

## Models

Les fonctions de gestion, de traitement et d’accès aux données sont réparties dans plusieurs fichiers. Généralement, un page possède un fichier modèle possédant les fonctions nécessaires. Cependant, certains fichiers (`brats_utils.py` et `cquest_utils.py`) ne correspondent pas à une unique page mais sont utilisés par plusieurs autres car leurs fonctions sont nécessaires plusieurs fois.

### brats_utils

`**get_processed_data_from_niftis_folder**(folder_id: str, slider_value: int, axe: str,                                          only_mask: bool) -> np.ndarray and int`

Permet de récupérer les fichiers NIfTI présents dans le dossier `tmp/user_compare/<folder_id>`. La fonction va d’abord décompresser les images (si besoin), puis va les charger une à une sur la tranche `slider_value` par rapport à l’axe `axe`. Une nouvelle image est générée représentant la moyenne de toutes les autres, et un masque des différence est ajouté. Ce masque contient des pixels allant du transparent au rouge en fonction du nombre de différences entre les images chargées sur chaque pixel. La fonction retourne ensuite le masque ajouté à l’image moyenne (en fonction du paramètre `only_mask`) ainsi que le nombre de tranche du volume sur l’axe `axe`.

`**get_global_brats_experiment_data**(experiment_id: int, file: str = None) -> pd.DataFrame and list`

Récupère les données agrégées/traitées des résultats d’une expérience BraTS. Récupère l’emplacement des données sur Girder (grâce au `girder_id`) en effectuant une requête en base de données. Conserve uniquement les données correspondant au fichier `file` si précisé et les retourne accompagné de la liste des fichiers mentionnées dans les données.

`**build_difference_image_ssim**(img1: any, img2: any, k1: float = 0.01, k2: float = 0.03, sigma: float = 1.5) -> np.ndarray and float`

Génère une image et un score grâce à la méthode **SSIM**. Fait appel à la librairie `skimage` pour la fonction **SSIM** et traite les données pour les retourner.

**`compute_psnr**(array1: np.ndarray, array2: np.ndarray) -> float or str`

Pré-traite les données pour avoir le bon format puis calcul la mesure **PSNR**. Dans le cas d’un PSNR infini, retourne “infinite”.

`**get_processed_data_from_niftis**(id1: str, id2: str, axe: str, slider_value: int) -> ndarray and ndarray and tuple and Image and Image:`

Charge les images NIfTI à partir des identifiants `id1` et `id2` passés en paramètres selon l’axe `axe` au niveau de la couche `slider_value`. Retourne ensuite les deux images 2D chargées, l’indice de la couche maximum selon l’axe demandé et les deux volumes des images .

### ************************cquest_utils************************

**`get_cquest_experiment_data**(experiment_id: int) -> pd.DataFrame`

Utilise l’identifiant `experiment_id` pour retrouver une expérience en base de données et récupérer son identifiant Girder. Les données de l’expérience sont ensuite téléchargées (fichier feather), traitées pour transformer les champs string en valeurs numériques puis renvoyées.

`**read_cquest_file**(file_uuid: str) -> pd.DataFrame`

Retourne les données d’un fichier sous forme de dataFrame à partir de son id (nom du fichier stocké localement).

`**get_metadata_cquest**(exp_id: int) -> list`

Retourne les métadonnées des fichiers contenus dans les workflows contenus dans le dossier de l’expérience `exp_id`.