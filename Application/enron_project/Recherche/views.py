from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import User, User_Email, Mail,Mail_Receiver
from django.db import connection
import pandas as pd
import numpy as np
import json
import matplotlib
from .Auxiliaire import sql_asker, find_max_and_where, visuel_detail1, visuel_couple,recu_interne,envoi_interne,time_rep,envoi_totale,received_rep



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
    contact_list=list((set(contact_as_sender_in)|set(contact_as_receiver_in)))
    contact_si,contact_ri=[i.id for i in set(contact_as_sender_in)],[i.id for i in set(contact_as_receiver_in)]
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
    try:
        wow=round(len(contact_as_receiver_in)/(len(contact_as_receiver_in)+len(contact_as_receiver_out)),3)*100
    except:
        wow='Pas de message, pas de ratio'
    try:
        serious=round(len(contact_as_sender_in)/(len(contact_as_sender_in)+len(contact_as_sender_out)),3)*100
    except:
        serious='Pas de message, pas de ratio'
    try:
        test=visuel_detail1(user_id,contact_si,contact_ri)
    except:
        test='Pas de message'
    try:
        centset=round((avg_msd[0][0]/avg_msd[0][1].total_seconds())*3600*24,2)
    except:
        centset='Pas de message, pas d info'
    try:
        ilmanquiquine=round((avg_mrd[0][0]/avg_mrd[0][1].total_seconds())*3600*24,2)
    except:
        ilmanquiquine='Toujours rien déso'
    context = {
        'user_nom': user.nom,
        'user_prenom':user.prenom,
        'user_categorie':user.categorie,
        'user_email':[i.adr_Mail for i in User_Email.objects.filter(user_id=user.id)],
        'user_contact':user_contact,
        'user_s_tot':len(contact_as_sender_in)+len(contact_as_sender_out),
        'user_s_in':len(contact_as_sender_in),
        'user_s_out':len(contact_as_sender_out),
        'ratio_s_i_tot':serious,
        'user_r_tot':len(contact_as_receiver_in)+len(contact_as_receiver_out),
        'user_r_in':len(contact_as_receiver_in),
        'user_r_out':len(contact_as_receiver_out),
        'ratio_r_i_tot':wow,
        'paginate':True,
        'avg_time_rep':avg_time_rep,
        'avg_msd':centset,
        'avg_mrd':ilmanquiquine,
        'msg_diff':avg_msd[0][0],
        'test':test
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
    if request.method == 'POST':
        if type(request.POST.get('bdate'))==type('a') and request.POST.get('bdate') !='' :
            bdate = " AND t3.date >'" + request.POST.get('bdate')+"' "
        else:
            bdate=''
        if type(request.POST.get('edate'))==type('a') and request.POST.get('edate') !='':
            edate =  " AND t3.date <'" + request.POST.get('edate')+"' "
        else:
            edate=''
        if type(request.POST.get('smin'))==type('a'):
            try:
                smin=int(request.POST.get('smin'))
            except:
                smin=0
        else:
            smin=0
        if (type(request.POST.get('smax'))==type('a')):
            try:
                smax=int(request.POST.get('smax'))
            except:
                smax=10**10
        else:
            smax=10**10
        if type(request.POST.get('qt'))==type('a'):
            try:
                qt = int(request.POST.get('qt'))
            except:
                qt=10
        else:
            qt=10
    else:
        bdate,edate,smin,smax,qt='','',0,10**10,10
    user_list=User.objects.exclude(nom='NotInEnron')
    grille=pd.DataFrame(columns=[i.id for i in user_list],index=[i.id for i in user_list]).fillna(0)
    list_id= [ i.id for i in user_list ]
    for ligne in list(grille.index):
        try:
            req=sql_asker('''SELECT t6.id,count(t6.id)
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom!='NotInEnron' '''+bdate+edate+' GROUP BY t6.id;',ligne)
        except:
            req=sql_asker('''SELECT t6.id,count(t6.id)
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom!='NotInEnron'  GROUP BY t6.id;''',ligne)
        for col_val in req:
            grille.loc[ligne].loc[col_val[0]]=col_val[1]
    grille_finale=grille+grille.transpose(copy=True)
    grille_finale=np.triu(grille_finale,1)
    construction=[(i[0],(User.objects.get(id=list_id[i[1][0]]),User.objects.get(id=list_id[i[1][1]]))) for i in find_max_and_where(grille_finale,qt,smax,smin) ]
    class PourTemplate:
        def __init__(self,var):
            self.valeur=int(var[0])
            self.user1=var[1][0]
            self.user2=var[1][1]
    ready=[PourTemplate(i) for i in construction]
    visu=visuel_couple(ready)
    context={
        'data':ready,
        'p':(smin,smax),
        'visu':visu
    }
    return render(request, 'Recherche/couple.html', context)




def employe(request):
    users=User.objects.exclude(nom='NotInEnron')
    if request.method == 'POST':
        if type(request.POST.get('bdate'))==type('a') and request.POST.get('bdate') !='' :
            bdate = " AND t3.date >'" + request.POST.get('bdate')+"' "
        else:
            bdate=''
        if type(request.POST.get('edate'))==type('a') and request.POST.get('edate') !='':
            edate =  " AND t3.date <'" + request.POST.get('edate')+"' "
        else:
            edate=''
        if type(request.POST.get('smin'))==type('a'):
            try:
                smin=int(request.POST.get('smin'))
            except:
                smin=0
        else:
            smin=0
        if (type(request.POST.get('smax'))==type('a')):
            try:
                smax=int(request.POST.get('smax'))
            except:
                smax=10**10
        else:
            smax=10**10
        if type(request.POST.get('stmin'))==type('a'):
            try:
                stmin=int(request.POST.get('stmin'))
            except:
                stmin=0
        else:
            smin=0
        if (type(request.POST.get('stmax'))==type('a')):
            try:
                stmax=int(request.POST.get('stmax'))
            except:
                stmax=10**10
        else:
            stmax=10**10
        if type(request.POST.get('sdmin'))==type('a'):
            try:
                sdmin=int(request.POST.get('sdmin'))
            except:
                sdmin=0
        else:
            sdmin=0
        if (type(request.POST.get('sdmax'))==type('a')):
            try:
                sdmax=int(request.POST.get('sdmax'))
            except:
                sdmax=10**10
        else:
            stmax=10**10    
        if type(request.POST.get('qt'))==type('a'):
            try:
                qt = int(request.POST.get('qt'))
            except:
                qt=10
        else:
            qt=10
    else:
        bdate,edate,smin,smax,stmin,stmax,sdmin,sdmax,qt='','',0,10**10,0,10**10,0,10**10,10
    com_interne=[recu_interne(bdate,edate),envoi_interne(bdate,edate)]
    time=time_rep(bdate,edate)
    difu=[envoi_totale(bdate,edate),received_rep(bdate,edate)]
    dic_com={i[1]:i[0] for i in com_interne[0] }
    for t in com_interne[1]:
        try:
            dic_com[t[1]]+=t[0]
        except:
            pass
    dic_time={i[1]:i[0] for i in time}
    dic_difu={i[1]:i[0] for i in difu[0] }
    for t in difu[1]:
        try:
            dic_difu[t[1]]+=-t[0]
        except:
            pass
    class SuperInformationsOnUser:
        def __init__(self,user):
            self.user=user
            try:
                self.time=dic_time[user.id]
            except:
                self.time=None
            try:
                self.esr=dic_difu[user.id]
            except:
                self.esr=0
            try:
                self.comi=dic_com[user.id]
            except:
                self.comi=0
        def __str__(self):
            return self.user.nom+' '+str(self.comi)
    super_users=[SuperInformationsOnUser(i) for i in users]
    cl_comi=list(filter(lambda x: ((x.comi > smin)&(x.comi<smax)), sorted(super_users, key=lambda x: x.comi, reverse=True)))
    try:
        cl_comi=cl_comi[:qt]
    except:
        pass
    cl_esr=list(filter(lambda x: ((x.esr > sdmin)&(x.esr<sdmax)), sorted(super_users, key=lambda x: x.esr, reverse=True)))
    try:
        cl_esr=cl_esr[:qt]
    except:
        pass
    cl_time=list(filter(lambda x: ((x.time.total_seconds() > stmin)&(x.time.total_seconds()<stmax)), sorted(list(filter(lambda x: x.time!=None,super_users)), key=lambda x: x.time.total_seconds() )))
    try:
        cl_time=cl_time[:qt]
    except:
        pass 
    context={
        'comu':cl_comi,
        'difu':cl_esr,
        'time':cl_time,
        'envoi':dic_com


    }
    return render(request, 'Recherche/employe.html', context)



def jour(request):
    if request.method == 'POST':
        if type(request.POST.get('bdate'))==type('a') and request.POST.get('bdate') !='' :
            bdate = " AND t1.date >'" + request.POST.get('bdate')+"' "
        else:
            bdate=''
        if type(request.POST.get('edate'))==type('a') and request.POST.get('edate') !='':
            edate =  " AND t1.date <'" + request.POST.get('edate')+"' "
        else:
            edate=''
        if type(request.POST.get('smin'))==type('a'):
            try:
                smin=int(request.POST.get('smin'))
            except:
                smin=0
        else:
            smin=0
        if (type(request.POST.get('smax'))==type('a')):
            try:
                smax=int(request.POST.get('smax'))
            except:
                smax=10**10
        else:
            smax=10**10
        if type(request.POST.get('qt'))==type('a'):
            try:
                qt = int(request.POST.get('qt'))
            except:
                qt=10
        else:
            qt=10
    else:
        bdate,edate,smin,smax,qt='','',0,10**10,10
    try:
        req=sql_asker('''SELECT DATE(t1.date), count(t1.id)
    FROM "Recherche_mail" as t1
    WHERE DATE(t1.date)>'1990-01-01' '''+bdate+edate+''' 
    GROUP BY DATE(t1.date) ORDER BY COUNT(t1.id) DESC;''',"")
    except:
        req=sql_asker('''SELECT DATE(t1.date), count(t1.id)
    FROM "Recherche_mail" as t1
    WHERE DATE(t1.date)>'1990-01-01'
    GROUP BY DATE(t1.date) ORDER BY COUNT(t1.id) DESC;''',"")
    jours=[]
    for val in req:    
        if val[1]>smin and val[1]<smax:
            jours.append((val[0],val[1]))
    try:
        jours=jours[:qt]
    except:
        pass
    class PourTemplate:
        def __init__(self,var):
            self.date=var[0]
            self.nbMails=var[1]
    data=[PourTemplate(i) for i in jours]
    context={
        'data':data
    }
    return render(request, 'Recherche/jour.html', context)