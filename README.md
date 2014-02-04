import
======

xmlrpc script to insert client into an openerp 7 database

##TODO:

* generalize for res.partner (suppliers, users, clients, ...)
* later, the script will be able to insert in another tables (res.user for example) and to connect partners together (contacts into companies for example)

**draft schema :**

- input: clients.csv, suppliers.csv, users.csv
- output: res.partner, res.user