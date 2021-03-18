from django.db import models

# Create your models here.

class Employe(models.Model):
      id = models.AutoField(primary_key=True)
      adrMail = models.EmailField(30)
      categorie = models.CharField(3)
      nom =  models.CharField(15)
      prenom = models.CharField(15)




class Email(models.Model):
      id = models.AutoField(primary_key=True)
      message_id = models.CharField(22)
      date = models.DateTimeField()
      objet = models.CharField(30)
      texte = models.TextField()
      expediteur = models.EmailField(30)



class Destination(models.Model):
      id = models.AutoField(primary_key=True)
      type = models.CharField(3)
      employe_id = models.ForeignKey(
          'Employe',
          on_delete=models.CASCADE,
          )
      email_id = models.ForeignKey(
          'Email',
          on_delete=models.CASCADE,
          )