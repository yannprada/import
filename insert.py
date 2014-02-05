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

# prepare the relationnal data
relationnal_data = {
    'title': {
        'table_name': 'res.partner.title',
        'column_name': 'title',
        'data': {},
    },
    'country': {
        'table_name': 'res.country',
        'column_name': 'country_id',
        'data': {},
    },
}

# request the database and populate the data fields
for key in relationnal_data:
    obj = relationnal_data[key]
    table = obj['table_name']
    ids = sock.execute(dbname, uid, password, table, 'search', [])
    data = sock.execute(dbname, uid, password, table, 'read', ids, ['id', 'name'])
    # use the values of a list of objects like [{'id': someId, 'name': someName}, ...]
    # and insert into an object like {someName: someId, ...}
    for item in data:
        relationnal_data[key]['data'][item['name']] = item['id']

# names of columns must be exactly the same as those defined here (edit here if necessary, but be sure to edit data as well)
keys = ['ref','title','name','street','zip','city','country','phone','mobile','fax','email','website','customer','is_company']


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
                name = row[key]
                if not name:
                    res_partner_data[relationnal_data[key]['column_name']] = ''
                else:
                    res_partner_data[relationnal_data[key]['column_name']] = relationnal_data[key]['data'][name]
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

