from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import User, User_Email, Mail,Mail_Receiver
from django.db import connection
import pandas as pd
import numpy as np
import json
def sql_asker(query,param):
    with connection.cursor() as cursor:
        cursor.execute(query, [param])
        row = cursor.fetchall()
    return row

def find_max_and_where(array,hmany):
    val_pos=[]
    while hmany>0:
        val=np.amax(array)
        pos=list(zip(*np.where(array == val)))
        val_pos.append((val,pos))
        for i in pos:
            array[i[0]][i[1]]=0
            hmany+=-1
    return val_pos



def index(request):
    users = User.objects.exclude(nom='NotInEnron')[:12]
    context = {
        'users': users
    }
    return render(request, 'Recherche/index.html', context)

def listing(request):
    users_list = User.objects.exclude(nom='NotInEnron').order_by('nom')
    paginator = Paginator(users_list, 9)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'users': users,
        'paginate': True
    }
    return render(request, 'Recherche/listing.html', context)

def detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    contact_as_sender_in=User.objects.raw('''SELECT t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t5."adr_Mail" ~ '@enron.com$';''',[user.id])
    contact_as_receiver_in=User.objects.raw('''SELECT t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t6.id=%s AND t2."adr_Mail" ~ '@enron.com$';''',[user.id])
    contact_as_receiver_out=User.objects.raw('''SELECT t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t6.id=%s AND t2."adr_Mail" !~ '@enron.com$';''',[user.id])
    contact_as_sender_out=User.objects.raw('''SELECT t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t5."adr_Mail" !~ '@enron.com$';''',[user.id])
    contact_list=list(set(contact_as_sender_in)|set(contact_as_receiver_in))
    paginator = Paginator(contact_list, 6)
    page = request.GET.get('page')
    try:
        user_contact = paginator.page(page)
    except PageNotAnInteger:
        user_contact = paginator.page(1)
    except EmptyPage:
        user_contact = paginator.page(paginator.num_pages)
    avg_time_rep=sql_asker('''SELECT AVG(t3.date-t3."Mad")
FROM "Recherche_user" t1
JOIN "Recherche_user_email" t2 ON t1.id = t2.user_id_id
JOIN "Recherche_mail" t3 ON t2.id = t3.mail_user_id_id
WHERE t1.id=%s AND t3.is_a_response=true AND t3."Mad" > '1901-01-01' AND t3.date > t3."Mad";''',user_id)[0][0]
    avg_msd=sql_asker('''SELECT count(t3."id") ,(MAX (t3.date)-MIN(t3.date))
FROM "Recherche_user" t1
JOIN "Recherche_user_email" t2 ON t1.id = t2.user_id_id
JOIN "Recherche_mail" t3 ON t2.id = t3.mail_user_id_id
WHERE t1.id=%s;''',user_id)
    avg_mrd=sql_asker('''SELECT COUNT(t3.id),(MAX(t4.date)-MIN(t4.date))
FROM "Recherche_user" t1
JOIN "Recherche_user_email" t2 ON t1.id = t2.user_id_id
JOIN "Recherche_mail_receiver" t3 ON t2.id = t3.user_mail_id_id
JOIN "Recherche_mail" t4 ON t3.mail_id_id=t4.id
WHERE t1.id=%s;''',user_id)
    context = {
        'user_nom': user.nom,
        'user_prenom':user.prenom,
        'user_categorie':user.categorie,
        'user_email':[i.adr_Mail for i in User_Email.objects.filter(user_id=user.id)],
        'user_contact':user_contact,
        'user_s_tot':len(contact_as_sender_in)+len(contact_as_sender_out),
        'user_s_in':len(contact_as_sender_in),
        'user_s_out':len(contact_as_sender_out),
        'ratio_s_i_tot':round(len(contact_as_sender_in)/(len(contact_as_sender_in)+len(contact_as_sender_out)),3)*100,
        'user_r_tot':len(contact_as_receiver_in)+len(contact_as_receiver_out),
        'user_r_in':len(contact_as_receiver_in),
        'user_r_out':len(contact_as_receiver_out),
        'ratio_r_i_tot':round(len(contact_as_receiver_in)/(len(contact_as_receiver_in)+len(contact_as_receiver_out)),3)*100,
        'paginate':True,
        'avg_time_rep':avg_time_rep,
        'avg_msd':round((avg_msd[0][0]/avg_msd[0][1].total_seconds())*3600*24,2),
        'avg_mrd':round((avg_mrd[0][0]/avg_mrd[0][1].total_seconds())*3600*24,2),
        'msg_diff':avg_msd[0][0]
    }
    return render(request, 'Recherche/detail.html', context)

def search(request):
    query = request.GET.get('query')
    if not query:
        users = User.objects.exclude(nom='NotInEnron')
    else:
        # title contains the query is and query is not sensitive to case.
        users = User.objects.filter(nom__icontains=query).exclude(nom='NotInEnron')
    title = "Résultats pour la requête %s"%query
    context = {
        'users': users,
        'title': title
    }
    return render(request, 'Recherche/search.html', context)

def couple(request):

    user_list=User.objects.exclude(nom='NotInEnron')
    grille=pd.DataFrame(columns=[i.id for i in user_list],index=[i.id for i in user_list]).fillna(0)
    for ligne in list(grille.index):
            req=sql_asker('''SELECT t6.id,count(t6.id)
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom!='NotInEnron' GROUP BY t6.id;''',ligne)
            for col_val in req:
                grille.loc[ligne].loc[col_val[0]]=col_val[1]
    grille_finale=grille+grille.transpose(copy=True)
    grille_finale=np.triu(grille_finale,1)
    l,c=np.shape(grille_finale)
    grille_finale=np.concatenate((np.zeros(l).reshape(1,l),grille_finale),axis=0)
    grille_finale=np.concatenate((np.zeros(c+1).reshape(1+c,1),grille_finale),axis=1)
    construction=[(i[0],(User.objects.get(id=i[1][0][0]),User.objects.get(id=i[1][0][1]))) for i in find_max_and_where(grille_finale,10) ]
    class PourTemplate:
        def __init__(self,var):
            self.valeur=int(var[0])
            self.user1=var[1][0]
            self.user2=var[1][1]
    ready=[PourTemplate(i) for i in construction]
    context={
        'data':ready
    }
    return render(request, 'Recherche/couple.html', context)




def employe(request):
    users=User.objects.exclude(nom='NotInEnron')
    nombre_de_mail_externe=[(i,len(User.objects.raw('''SELECT t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom='NotInEnron';''',[i]))) for i in range(0,len(users))]
    nombre_de_mail_interne=[(i,len(User.objects.raw('''SELECT t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom!='NotInEnron';''',[i]))) for i in range(0,len(users))]
    context={
        'n':nombre_de_mail_externe,
        'm':nombre_de_mail_interne


    }
    return render(request, 'Recherche/employe.html', context)



def jour(request):
    query = request.GET.get('query')
    if not query:
        users = User.objects.exclude(nom='NotInEnron')
    else:
        # title contains the query is and query is not sensitive to case.
        users = User.objects.filter(nom__icontains=query).exclude(nom='NotInEnron')
    title = "Résultats pour la requête %s"%query
    data=users[1]
    context = {
        'users': users,
        'title': title,
        'p':158,
        'user':data
    }
    return render(request, 'Recherche/jour.html', context)