from Recherche.models import User, User_Email, Mail,Mail_Receiver
import xml.etree.ElementTree as ET
import os, maya,datetime
from email.parser import Parser

liste_user=[]
liste_addresse=[]
tree = ET.parse('../../Utile/employes_enron.xml')
root = tree.getroot()
for user in root.findall('employee'):
    role = user.get('category')
    if type(role)==type('str'):
        utilisateur=User(nom=user.find('lastname').text,prenom=user.find('firstname').text,categorie=role)
    else:
        utilisateur=User(nom=user.find('lastname').text,prenom=user.find('firstname').text,categorie='Employee')
    liste_user.append(utilisateur)
    for neighbor in user.iter('email'):
        addresse=User_Email(user_id=utilisateur,adr_Mail=neighbor.attrib['address'])
        liste_addresse.append(addresse)

for people in liste_user:
    people.save()
for add in liste_addresse:
    add.save()
utilisateur=User(nom='NotInEnron',prenom='NotInEnron',categorie='NotInEnron')
utilisateur.save()