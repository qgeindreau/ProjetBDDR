from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import User, User_Email, Mail,Mail_Receiver

def index(request):
    users = User.objects.filter()[:12]
    context = {
        'users': users
    }
    return render(request, 'Recherche/index.html', context)

def listing(request):
    users_list = User.objects.filter().order_by('nom')
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
WHERE t1.id=%s AND t6.prenom!='NotInEnron';''',[user.id])
    contact_as_receiver_in=User.objects.raw('''SELECT t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t6.id=%s AND t1.prenom!='NotInEnron';''',[user.id])
    contact_as_receiver_out=User.objects.raw('''SELECT t1.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t6.id=%s AND t1.prenom='NotInEnron';''',[user.id])
    contact_as_sender_out=User.objects.raw('''SELECT t6.id
FROM "Recherche_user" AS t1 
	JOIN "Recherche_user_email" AS t2 ON t1.id = t2.user_id_id
	JOIN "Recherche_mail" AS t3 ON t2.id =t3.mail_user_id_id
	JOIN "Recherche_mail_receiver" AS t4 ON t3.id=t4.mail_id_id
	JOIN "Recherche_user_email" AS t5 ON t4.user_mail_id_id=t5.id
	JOIN "Recherche_user" AS t6 ON t6.id = t5.user_id_id
WHERE t1.id=%s AND t6.prenom='NotInEnron';''',[user.id])

    context = {
        'user_nom': user.nom,
        'user_prenom':user.prenom,
        'user_categorie':user.categorie,
        'user_email':[i.adr_Mail for i in User_Email.objects.filter(user_id=user.id)],
        'user_contact':set(contact_as_sender_in)|set(contact_as_receiver_in),
        'user_s_tot':len(contact_as_sender_in)+len(contact_as_sender_out),
        'user_s_in':len(contact_as_sender_in),
        'user_s_out':len(contact_as_sender_out),
        'ratio_s_i_tot':round(len(contact_as_sender_in)/(len(contact_as_sender_in)+len(contact_as_sender_out)),3)*100,
        'user_r_tot':len(contact_as_receiver_in)+len(contact_as_receiver_out),
        'user_r_in':len(contact_as_receiver_in),
        'user_r_out':len(contact_as_receiver_out),
        'ratio_r_i_tot':round(len(contact_as_receiver_in)/(len(contact_as_receiver_in)+len(contact_as_receiver_out)),3)*100,
    }
    # solidays
    return render(request, 'Recherche/detail.html', context)

def search(request):
    query = request.GET.get('query')
    if not query:
        users = User.objects.all()
    else:
        # title contains the query is and query is not sensitive to case.
        users = User.objects.filter(nom__icontains=query)
    title = "Résultats pour la requête %s"%query
    context = {
        'users': users,
        'title': title
    }
    return render(request, 'Recherche/search.html', context)
