"""
A simple script utilising pglib.
Execute the script and when prompted provide the table name.
The script loops through all the ENM databases and displays the first
database which contains that table.
To return all the databases with that table remove the break from the
for loop in the main() method
"""
from past.builtins import raw_input
from pyu.log import log
from pyu.os.shell.local import LocalShellClient
# pylint: disable=E0611
from pyu.ui.visual.colour import Yellow, Green, Blue, Grey
from pyu.ui.visual.format.shortcuts import box, br, span

from pglib.env.credentials import credentials
from pglib.postgres import PsqlClient, PostgresSession


def is_table_in_db(shell, db, table):
    span(Blue("Checking if %s contains %s table." % (db, table)))
    psql = PsqlClient(shell, database=db)
    query = u"""
            SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 
            'pg_catalog' AND schemaname != 'information_schema';
            """
    result_set = psql.runq(query)
    return table in result_set


def get_all_dbs(shell):
    with PostgresSession() as psql:
        result_set = psql.get_dbs(
            ignore_dbs=['template0', 'template1', 'postgres'])
        log.debug('Databases: \n%s\n' % result_set, stdout=True)
        return result_set


def main():
    shell = LocalShellClient()
    log.setup_syslog('PG_Table_Finder', verbose=True)
    credentials.setup(shell.os.sg.pg.credentials_class)

    br()
    table = raw_input('Please enter the table you wish to find: ').lower()
    table = 'pm_rop_info' if not table else table
    print(table)
    found = False
    dbs = get_all_dbs(shell)
    for db in dbs:
        if is_table_in_db(shell, db, table):
            span(Yellow('%s contains %s' % (db, table)))
            found = True
            break
    if not found:
        log.error('No database contains the table: %s' % table, stdout=True)


if __name__ == '__main__':
    main()
