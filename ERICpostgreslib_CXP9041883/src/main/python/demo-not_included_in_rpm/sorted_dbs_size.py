from pyu.os.shell.local import LocalShellClient

from pglib.db.database import PgStore

shell = LocalShellClient()
pg_store = PgStore(shell)
db_list = pg_store.databases


print('-' * 50)
for db in db_list:
    print('%s %s' % (db.name, db.size))
print('-' * 50)


print('*' * 50)
sorted_dbs = sorted(db_list, key=lambda d: d.size, reverse=True)
print(sorted_dbs)
print('*' * 50)
