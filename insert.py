# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys
import xmlrpclib
import time
import csv

beginning = time.time()

if len(sys.argv) < 5:
    print('''
Usage:
    python insert.py [host] [database] [password] [file.csv]
''')
    sys.exit()

uid = 1
host = sys.argv[1]
dbname = sys.argv[2]
password = sys.argv[3]
input_name = sys.argv[4]


# config ##################################

input_kwargs = {
    'delimiter': ',',
    'quotechar': "'",
    'quoting': csv.QUOTE_MINIMAL,
    'lineterminator': '\n',
}

# names of columns must be exactly the same as those defined here (edit here if necessary, but be sure to edit data as well)
keys = ['ref','title','name','street','zip','city','country','phone','mobile','fax','email','website','customer','is_company']

###########################################

# connect
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
        obj['data'][item['name']] = item['id']

def message(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

with open(input_name, 'r') as input_file:
    cr = csv.DictReader(input_file, **input_kwargs)
    line = 0
    for row in cr:
        line += 1
        message(str(line) + ' Adding client: ' + row['name'] + ' ...')
        res_partner_data = {}
        for key in keys:
            value = row[key]
            # handle relationnal values
            if key in relationnal_data:
                if not value:
                    res_partner_data[relationnal_data[key]['column_name']] = ''
                else:
                    res_partner_data[relationnal_data[key]['column_name']] = relationnal_data[key]['data'][value]
            # handle other values
            else:
                # handle boolean values quoted
                if value in ['True', 'False']:
                    value = eval(value)
                
                res_partner_data[key] = value or False
        # insert values
        res_partner_id = sock.execute(dbname, uid, password, 'res.partner', 'create', res_partner_data)
        message('... done with id: ' + str(res_partner_id) + '\n')

end = time.time()
seconds = end - beginning

message('\n' + str(line) + ' clients added in ' + time.strftime('%H:%M:%S', time.gmtime(seconds)) + '\n')

