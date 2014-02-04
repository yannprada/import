import
======

xmlrpc script to insert client into an openerp 7 database

##TODO:
* generalize for res.partner (suppliers, users, clients, ...)
* draft schema:
                    clients.csv     >
                    supplier.csv    >> insert.py
                    users.csv       >
* later, the script will be able to insert in another tables (res.user for example) and to connect partners together (contacts into companies for example)