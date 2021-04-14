from email.parser import Parser 
from dateutil.parser import parse
import datetime, maya, pytz
from pytz import timezone
with open('../../Utile/2.txt', "r") as f:
    data = f.read() 
email = Parser().parsestr(data)

def conv_time(txt):
    return maya.parse(txt).datetime()
def conv_time2(txt):
    return parse(txt).astimezone(timezone('UTC'))

test='Tue, 29 Aug 2000 1:50:00 -0700 (PDT)'

print(conv_time(test))
print(conv_time2(test))
