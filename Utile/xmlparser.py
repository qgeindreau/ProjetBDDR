import xml.etree.ElementTree as ET
tree = ET.parse('Utile/employes_enron.xml')
root = tree.getroot()
for user in root.findall('employee'):
    role = user.get('category')
    if type(role)!='str':
        role='Employee'
    full_name = user.find('lastname').text + ' '+user.find('firstname').text
    email=user.get('address')
    for neighbor in user.iter('email'):
        print(neighbor.attrib)
    print(full_name, role,email)