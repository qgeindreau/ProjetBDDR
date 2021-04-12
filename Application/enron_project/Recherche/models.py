from django.db import models

# Create your models here.

class User(models.Model):
    categorie = models.CharField(20)
    nom =  models.CharField(20)
    prenom = models.CharField(20)
      
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
    date = models.DateTimeField()
    objet = models.CharField(30)
    body = models.TextField()
    is_a_response = models.BooleanField()
    mail_user_id = models.ForeignKey(
          User_Email,
          on_delete=models.CASCADE,
          ) #Id de celui qui envoie
    def __str__(self):
        return "Objet: "+ self.objet


class Mail_Receiver_in(models.Model):
    mail_id = models.ForeignKey(
        Mail,
        on_delete=models.CASCADE,
        )
    user_mail_id = models.ForeignKey(
        User_Email,
        on_delete=models.CASCADE,
        ) #Id de celui qu recoit
        def __str__(self):
            return "Mail:"+self.mail_id+'Add:'+self.user_mail_id
class Mail_Receiver_in(models.Model):
    mail_id = models.ForeignKey(
        Mail,
        on_delete=models.CASCADE,
        )
    email=models.EmailField()