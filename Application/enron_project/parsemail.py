from email.parser import Parser 
import datetime, maya
import re
def conv_time(txt):
    return maya.parse(txt).datetime()
def find_date(email):
        parse_d=re.compile(r'Sent:(?P<Date>.+)')
        try:
            date1=conv_time(parse_d.search(email.get_payload()).group('Date'))
        except:
            date1=conv_time('1900-01-01')
        parse_d=re.compile(r'@.+[.].+ on (?P<Date>.+)')
        try:
            date2=conv_time(parse_d.search(email.get_payload()).group('Date'))
        except:
            date2=conv_time('1900-01-01')
        return max(date2,date1)