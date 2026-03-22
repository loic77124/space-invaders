# Space Invaders – Contrôle par Vision (Mondor Loic,Somasuntharam Vaithehie)

Ce projet est une version du jeu Space Invaders contrôlée par les mouvements de la main via une webcam.

# Méthodologie initiale : Modèle CNN

Au départ, nous avons travaillé en binôme pour développer notre propre système de reconnaissance de gestes basé sur un réseau de neurones convolutif (CNN) :

-Collecte des données : capture d’images de gestes (LEFT, RIGHT, FIRE, ENTER, NOTHING) via OpenCV.

-Prétraitement : redimensionnement et normalisation des images.

-Entraînement du CNN : séparation des données en ensembles d’entraînement et de validation, ajustement des hyperparamètres.

-Test en temps réel : intégration dans le jeu pour détecter les gestes.

*Problèmes rencontrés:

-Reconnaissance instable selon la position de l’utilisateur.

-Les gestes LEFT et RIGHT fonctionnaient mieux lorsque seule la main était dans le champ de vision.

-Sensibilité à la luminosité et aux mouvements.

-Bugs divers rendant le contrôle du jeu peu fiable.

# Passage à MediaPipe HandLandmarker

Pour pallier ces limites et gagner du temps, nous avons choisi d’utiliser MediaPipe et son modèle HandLandmarker.

*Avantages:

-Détection fiable de la main en temps réel.

-Contrôle fluide et intuitif pour le jeu.

-Téléchargement automatique du modèle si nécessaire.

Nous avons également travaillé sur la même machine pour optimiser le temps. C’est pourquoi, dans les commits, seule une personne apparaît, même si le travail a été réalisé en binôme.

# Téléchargement automatique

Lors du lancement, le module HandLandmarker se télécharge automatiquement si nécessaire.

#Contrôles du jeu

-Main ouverte : ENTER

-Deux doigts en l’air ou tendus : FIRE

-Poing fermé horizontal, déplacé à gauche ou à droite : LEFT ou RIGHT