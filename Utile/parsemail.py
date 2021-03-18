from email.parser import Parser
with open('2.txt', "r") as f:
    data = f.read()
    
email = Parser().parsestr(data)

print("\nTo: " , email['to'])
print("\n From: " , email['from'])
 
print("\n Subject: " , email['bcc'])