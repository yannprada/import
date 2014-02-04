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
host = 'http://172.16.1.73:8069'
dbname = sys.argv[2]
password = sys.argv[3]
input_name = sys.argv[1]
input_kwargs = {
    'delimiter': ',',
    'quotechar': "'",
    'quoting': csv.QUOTE_MINIMAL,
    'lineterminator': '\n',
}

sock = xmlrpclib.ServerProxy(host + '/xmlrpc/object')

res_partner_title_ids = sock.execute(dbname, uid, password, 'res.partner.title', 'search', [])
res_country_ids = sock.execute(dbname, uid, password, 'res.country', 'search', [])

relationnal_data = {
    'title': {
        'table_name': 'res.partner.title',
        'column_name': 'title',
        'data': sock.execute(dbname, uid, password, 'res.partner.title', 'read', res_partner_title_ids, []),
    },
    'country': {
        'table_name': 'res.country',
        'column_name': 'country_id',
        'data': sock.execute(dbname, uid, password, 'res.country', 'read', res_country_ids, []),
    },
}

# names of columns must be exactly the same as those defined here (edit here if necessary, but be sure to edit data as well)
keys = ['ref','title','name','street','zip','city','country','phone','mobile','fax','email','website','customer','is_company']


def search_id_by_name(data, name):
    '''
data: list of objects
name: value of the attribute 'name'
return: id of the object which match the value of the attribute 'name' provided
    '''
    for item in data:
        if item['name'] == name:
            return item['id']
    return None

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
            if key in relationnal_data:
                some_id = search_id_by_name(relationnal_data[key]['data'], row[key])
                if some_id is None:
                    print('\nUnknow value "' + str(row[key]) + '" for attribute "name" in table "' + relationnal_data[key]['table_name'] + '"')
                    res_partner_data[relationnal_data[key]['column_name']] = ''
                else:
                    res_partner_data[relationnal_data[key]['column_name']] = some_id
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

