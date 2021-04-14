from Recherche.models import User, User_Email, Mail,Mail_Receiver
import xml.etree.ElementTree as ET
import os,datetime
from email.parser import Parser
from dateutil.parser import parse
from pytz import timezone
def is_response(txt): #Renvoie 1 si c'est une réponse (càd si RE: est présent dans le subject)
    return not(txt.find('RE:')==-1 and txt.find('re:')==-1 and txt.find('Re:')==-1 )

path="../../Utile/maildir"
listdir_files = []
for dirpath, subdirs, files in os.walk(path):
    for x in files:
        if x.endswith("."):
            listdir_files.append(os.path.join(dirpath, x))
object_mail=[]
object_mr=[]

for _email in listdir_files:

    with open(_email,'r',errors='ignore') as f:
        data= f.read()
    email = Parser().parsestr(data)

    try:
        mail=Mail(date=parse(email['date']).astimezone(timezone('UTC')),objet=email['Subject'],is_a_response=is_response(email['Subject']),mail_user_id=User_Email.objects.filter(adr_Mail=email['From'])[0])
    except:
        new_address=User_Email(adr_Mail=email['From'],user_id=User.objects.filter(nom='NotInEnron')[0])
        new_address.save()
        mail=Mail(date=parse(email['date']).astimezone(timezone('UTC')),objet=email['Subject'],is_a_response=is_response(email['Subject']),mail_user_id=User_Email.objects.filter(adr_Mail=email['From'])[0])
    
    if type(email['to'])==type('str'):
        for receveur in email['to'].replace(' ','').replace('\n','').replace('\t','').split(',') :
            if receveur!='':
                try:        
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='to')
                except:
                    new_address=User_Email(adr_Mail=receveur,user_id=User.objects.filter(nom='NotInEnron')[0])
                    new_address.save()
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='to')
                object_mr.append(recc)
    if type(email['cc'])==type('str'):
        for receveur in email['cc'].replace(' ','').replace('\n','').replace('\t','').split(',') :
            if receveur!='':
                try:        
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='cc')
                except:
                    new_address=User_Email(adr_Mail=receveur,user_id=User.objects.filter(nom='NotInEnron')[0])
                    new_address.save()
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='cc')
                object_mr.append(recc)
    if type(email['bcc'])==type('str'):
        for receveur in email['bcc'].replace(' ','').replace('\n','').replace('\t','').split(','):
            if receveur!='':
                try:        
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='bcc')
                except:
                    new_address=User_Email(adr_Mail=receveur,user_id=User.objects.filter(nom='NotInEnron')[0])
                    new_address.save()
                    recc=Mail_Receiver(mail_id=mail,user_mail_id=User_Email.objects.filter(adr_Mail=receveur)[0],genre='bcc')
                object_mr.append(recc)
    object_mail.append(mail)

for mail2 in object_mail:
    mail2.save()
for ppl in object_mr:
    ppl.save()