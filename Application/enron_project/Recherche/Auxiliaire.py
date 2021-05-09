from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import User, User_Email, Mail,Mail_Receiver
from django.db import connection
import pandas as pd
import numpy as np
import json
from io import StringIO
import numpy as np
import plotly.graph_objs as go
import igraph as ig

pd.options.plotting.backend = "plotly"


def sql_asker(query,param):
    with connection.cursor() as cursor:
        cursor.execute(query, [param])
        row = cursor.fetchall()
    return row

def find_max_and_where(A,hmany,top,bot):
    val_pos=[]
    while hmany>0:
        try:
            val=A[(A<top) & (A>bot)].max()
            pos=list(zip(*np.where(A == val)))
            for i in pos:
                val_pos.append((val,i))
                A[i[0]][i[1]]=0
                hmany+=-1
        except:
            break
    return val_pos

def visuel_detail1(user_id,contact_s,contact_r):
    envoi=[sql_asker('''SELECT t6.nom,count(t6.id)
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id='''+user_id+ '''AND t6.id =%s AND t6.prenom!='NotInEnron'  GROUP BY t6.id;''',i) for i in contact_s ]
    recu=[sql_asker('''SELECT t1.nom,count(t6.id)
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.id ='''+user_id+ ''' AND t1.prenom!='NotInEnron'  GROUP BY t1.id;''',i) for i in contact_r ]
    srecu=pd.Series({i[0]:i[1] for i in [item for sublist in recu for item in sublist]})
    senvoi=pd.Series({i[0]:i[1] for i in [item for sublist in envoi for item in sublist]})
    df=pd.DataFrame({'Envoi':senvoi,'Recu':srecu})
    fig = df.plot.bar(x=df.columns,y=df.index)
    data = fig.to_html(full_html=False, default_height=500, default_width=550)
    return data

def visuel_couple(data):
    def graph(data):
        ppl=list(set([i.user1 for i in data])|set([i.user2 for i in data]))
        MonBeauGraph=ig.Graph()
        for i in ppl:
            MonBeauGraph.add_vertex(i.nom+'\n'+i.prenom,attr={'Name':i.nom+'\n'+i.prenom+'\n'+i.categorie})
        poid=[]
        for i in data:
                MonBeauGraph.add_edge(i.user1.nom+'\n'+i.user1.prenom,i.user2.nom+'\n'+i.user2.prenom)
                poid.append(i.valeur)
        return MonBeauGraph
    G=graph(data)
    titre='Un petit visuel en bonus ?'
    N=G.vcount()
    layt=G.layout('kk3d',dim=3)
    Edges=[e.tuple for e in G.es]
    Xn=[]
    Yn=[]
    Zn=[]
    Xe=[]
    Ye=[]
    Ze=[]
    symboles='diamond'
    Taille=5
    labels=G.vs()['name']
    colorgrp=1
    for k in range(N):
        Xn+=[layt[k][0]]
        Yn+=[layt[k][1]]
        Zn+=[layt[k][2]]
    for e in Edges:
        Xe+=[layt[e[0]][0],layt[e[1]][0],None]# x-coordinates of edge ends
        Ye+=[layt[e[0]][1],layt[e[1]][1],None]
        Ze+=[layt[e[0]][2],layt[e[1]][2],None]
    trace1=go.Scatter3d(x=Xe, y=Ye, z=Ze, mode='lines',line=dict(color='rgb(125,125,125)', width=5),hoverinfo='none')
    trace2=go.Scatter3d(x=Xn, y=Yn, z=Zn, mode='markers', name='membres', 
        marker=dict(symbol=symboles, size=Taille,color=colorgrp, 
        line=dict(color='rgb(50,50,50)', width=0.5)), text=labels, hoverinfo='text')
    axis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')

    layout = go.Layout(
         title=titre,
         width=500,
         height=500,
         showlegend=False,
         scene=dict(
             xaxis=dict(axis),
             yaxis=dict(axis),
             zaxis=dict(axis),
        ))

    data=[trace1, trace2]
    fig=go.Figure(data=data, layout=layout)
    visu = fig.to_html(full_html=False, default_height=500, default_width=550)
    return visu

def recu_interne(bdate,edate):
    try:
        recu=sql_asker('''SELECT COUNT(t1.id),t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t2."adr_Mail" ~'.+@enron.com$'AND t5."adr_Mail" ~'.+@enron.com$'AND t6.nom!='NotInEnron' '''+bdate+edate +'''GROUP BY t6.id ;''','')
    except:
        recu=sql_asker('''SELECT COUNT(t1.id),t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t2."adr_Mail" ~'.+@enron.com$'AND t5."adr_Mail" ~'.+@enron.com$'AND t6.nom!='NotInEnron' GROUP BY t6.id ;''','')
    return recu
def envoi_interne(bdate,edate):
    try:
        envoi=sql_asker('''SELECT COUNT(t6.id),t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t2."adr_Mail" ~'.+@enron.com$'AND t5."adr_Mail" ~'.+@enron.com$'AND t1.nom!='NotInEnron '''+bdate+edate + ''' GROUP BY t1.id ;''','')
    except:
        envoi=sql_asker('''SELECT COUNT(t6.id),t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t2."adr_Mail" ~'.+@enron.com$'AND t5."adr_Mail" ~'.+@enron.com$' AND t1.nom!='NotInEnron' GROUP BY t1.id ;''','')
    return envoi

def time_rep(bdate,edate):
    try:
        liste=sql_asker('''SELECT AVG(t3.date-t3."Mad"),t1.id
FROM "Recherche_user" t1
JOIN "Recherche_user_email" t2 ON t1.id = t2.user_id_id
JOIN "Recherche_mail" t3 ON t2.id = t3.mail_user_id_id
WHERE t3.is_a_response=true AND t3."Mad" > '1901-01-01' AND t3.date > t3."Mad"'''+bdate+edate+''' GROUP BY t1.id;''','')
    except:
        liste=sql_asker('''SELECT AVG(t3.date-t3."Mad"),t1.id
FROM "Recherche_user" t1
JOIN "Recherche_user_email" t2 ON t1.id = t2.user_id_id
JOIN "Recherche_mail" t3 ON t2.id = t3.mail_user_id_id
WHERE t3.is_a_response=true AND t3."Mad" > '1901-01-01' AND t3.date > t3."Mad"  GROUP BY t1.id;''','')
    return liste

def envoi_totale(bdate,edate):
    try:
        liste=sql_asker('''SELECT COUNT(t6.id),t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.nom!='NotInEnron' '''+bdate+edate+''' GROUP BY t1.id ;''','')
    except:
        liste=sql_asker('''SELECT COUNT(t6.id),t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.nom!='NotInEnron' GROUP BY t1.id ;''','')
    return liste
def received_rep(bdate,edate):
    try:
        liste=sql_asker('''SELECT COUNT(t1.id),t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t3.is_a_response=true'''+bdate+edate+ '''GROUP BY t6.id ;''','')
    except:
        liste=sql_asker('''SELECT COUNT(t1.id),t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t3.is_a_response=true GROUP BY t6.id ;''','')
    return liste