#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping
import requests#Module pour faire des requètes html
import tarfile #module pour déziper
import os #Module pour gérer les répértoires et fichier

def get_name(url):#fonction pour retrouver le nom d'un fichier en téléchargement
    URL=url.split("/")#On sépare l'url par /
    return URL[len(URL)-1]#On retourne la dernière partie de l'url




def download(url):#Fonction pour télécharger un fichier
    get = requests.get(url)#On fait la requete
    name=get_name(url)#On prend le nom
    open(name,'wb').write(get.content)#On recopie le contenu sur un fichier avec le nom obtenue (en mode 'rb' pour éviter les erreur)
    return

def dl_unzip(url):#Fonction pour télécharger et dezipper d un coup
    download(url)
    with tarfile.open(get_name( url )) as f:
        f.extractall()#On dézippe
    os.remove(get_name(url))#On supprime le fichier compresser

if __name__ == "__main__":
    dl_unzip()
