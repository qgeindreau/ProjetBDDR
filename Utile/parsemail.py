from email.parser import Parser 
import datetime
with open('Utile/2.txt', "r") as f:
    data = f.read()
    
email = Parser().parsestr(data)

date_time_str = email['date']
#date_time_obj = datetime.datetime.strptime(date_time_str, "%a, %d %B, %Y")


import maya

dt = maya.parse(date_time_str).datetime()
print(dt)
import maya
import datetime
def conv_time(txt):
    return maya.parse(txt).datetime()

print(conv_time(date_time_str))