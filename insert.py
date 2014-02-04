# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys
import xmlrpclib
import time
import csv

beginning = time.time()

if len(sys.argv) < 4:
    print('''
Usage:
    python insert.py [csv file name] [database name] [password]
''')
    sys.exit()

uid = 1
dbname = sys.argv[2]
password = sys.argv[3]
input_name = sys.argv[1]
input_kwargs = {
    'delimiter': ',',
    'quotechar': "'",
    'quoting': csv.QUOTE_MINIMAL,
    'lineterminator': '\n',
}

sock = xmlrpclib.ServerProxy('http://172.16.1.73:8069/xmlrpc/object')

res_partner_title_ids = sock.execute(dbname, uid, password, 'res.partner.title', 'search', [])
res_country_ids = sock.execute(dbname, uid, password, 'res.country', 'search', [])

data = {
    'title': sock.execute(dbname, uid, password, 'res.partner.title', 'read', res_partner_title_ids, []),
    'country': sock.execute(dbname, uid, password, 'res.country', 'read', res_country_ids, []),
}

# names of columns must be exactly the same as those defined here (edit here if necessary, but be sure to edit data as well)
keys = ['ref','title','name','street','zip','city','country','phone','mobile','fax','email','website','customer','is_company']

def search_id_by_name(data, name):
    for item in data:
        if item['name'] == name:
            return item['id']

with open(input_name, 'r') as input_file:
    cr = csv.DictReader(input_file, **input_kwargs)
    line = 0
    for row in cr:
        line += 1
        sys.stdout.write(str(line) + ' Adding client: ' + row['name'] + ' ...')
        sys.stdout.flush()
        res_partner_data = {}
        for key in keys:
            # handle relationnal values
            if key in ['title', 'country']:
                res_partner_data[key] = search_id_by_name(data[key], row[key]) or False
            else:
                # handle boolean values quoted
                if row[key] == 'True':
                    res_partner_data[key] = True
                elif row[key] == 'False':
                    res_partner_data[key] = False
                # handle all other values
                else:
                    res_partner_data[key] = row[key] or False
        res_partner_id = sock.execute(dbname, uid, password, 'res.partner', 'create', res_partner_data)
        sys.stdout.write('... done with id: ' + str(res_partner_id) + '\n')
        sys.stdout.flush()

end = time.time()
seconds = end - beginning

print
print(str(line) + ' clients added in ' + time.strftime('%H:%M:%S', time.gmtime(seconds))
)
print

