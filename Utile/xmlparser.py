def is_response(txt): #Renvoie 1 si c'est une réponse (càd si RE: est présent dans le subject)
    return not(txt.find('RE:')==-1 and txt.find('re:')==-1 and txt.find('Re:')==-1 )


print(is_response('Re:'))