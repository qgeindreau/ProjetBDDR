from django.db import models
from email.parser import Parser
from dateutil.parser import parse
# Create your models here.

class User(models.Model):
    categorie = models.CharField(max_length=20)
    nom =  models.CharField(max_length=20)
    prenom = models.CharField(max_length=20)
      
    def __str__(self):
        return 'Nom+: '+self.nom+' Prenom: '+self.prenom +' Categorie: ' +self.categorie

class User_Email(models.Model):
    user_id = models.ForeignKey(
          User,
          on_delete=models.CASCADE,
          )
    adr_Mail = models.EmailField(30)

    def __str__(self):
        return 'Addresse: '+self.adr_Mail

class Mail(models.Model):
    identifiant=models.CharField(max_length=300,unique=True)
    date = models.DateTimeField()
    objet = models.CharField(max_length=300)
    is_a_response = models.BooleanField()
    Mad=models.DateTimeField(blank=True,default='')
    mail_user_id = models.ForeignKey(
          User_Email,
          on_delete=models.CASCADE,
          ) #Id de celui qui envoie
    def __str__(self):
        return "Objet: "+ self.objet


class Mail_Receiver(models.Model):
    mail_id = models.ForeignKey(
        Mail,
        on_delete=models.CASCADE,
        )
    user_mail_id = models.ForeignKey(
        User_Email,
        on_delete=models.CASCADE,
        ) #Id de celui qu recoit
    genre = models.CharField(max_length=6)

    def __str__(self):
        return "Mail:"+self.mail_id+'Add:'+self.user_mail_id