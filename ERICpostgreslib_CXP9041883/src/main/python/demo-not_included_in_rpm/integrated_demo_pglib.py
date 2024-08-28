from pyu.log import log
from pyu.os.shell.local import LocalShellClient
# pylint: disable=E0611
from pyu.ui.visual.colour import Yellow, Green, Blue, Grey
from pyu.ui.visual.format.shortcuts import box, span

from pglib.env.credentials import credentials
from pglib.postgres import PsqlClient, PostgresSession


def demo_local_psql_client(shell):
    box('Get a Local PSQL connection')
    span(Yellow("psql = PsqlClient(LocalShellClient(), credentials.postgres)"
                "\nrs = psql.run('SELECT 1', headers=False)"))
    psql = PsqlClient(LocalShellClient(), credentials.postgres)
    rs = psql.run('SELECT 1', headers=False)
    log.debug('result: %s' % rs, stdout=True)
    span(Green('Connect to a Database flsdb'))
    span(Blue("psql2 = PsqlClient(LocalShellClient(), database='flsdb')\n "
              "query = 'SELECT filename FROM databasechangelog ORDER BY "
              "filename DESC LIMIT 1;'\nrs2 = psql2.run(query, headers=True)"))
    psql2 = PsqlClient(shell, database='flsdb')
    query = 'SELECT filename FROM databasechangelog ORDER BY filename ' \
            'DESC LIMIT 1;'
    rs2 = psql2.run(query, headers=True)
    log.debug('result with header: \n%s' % rs2, stdout=True)
    rs3 = psql2.runq(query)
    log.debug('result without headers: \n%s' % rs3, stdout=True)
    span(Yellow("Postgres Files: shell.os.sg.pg.files.pg_data_dir.size"))
    log.debug('Postgres Data Dir sizes: %s' %
              shell.os.sg.pg.files.pg_data_dir.size, stdout=True)


def demo_local_psycopg_psql_session(shell):
    box('Postgres Session - Pysycopg2')
    span(Grey('Ensure credentials are setup:'
              '\ncredentials.setup(shell.os.sg.pg.credentials_class)'))
    # P0stgreSQL11
    with PostgresSession(credential=('postgres', 'P0stgreSQL11'),
                         database='flsdb') as psql:
        query = 'SELECT filename FROM databasechangelog LIMIT 5;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchone(query)
        log.debug('Fetchone: %s\n' % rs, stdout=True)
        rs2 = psql.fetchall(query)
        log.debug('Fetchall: %s\n' % rs2, stdout=True)

    span(Yellow("Connect as a different user: \nwith PostgresSession"
                "(credential=('fls', 'fls123'), shell=shell, database='flsdb')"
                " as psql:"))
    with PostgresSession(credential=('fls', 'fls123'),
                         database='flsdb') as psql:
        query = 'SELECT COUNT(*) FROM databasechangelog;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchone(query)
        log.debug('Fetchone as fls user: %s\n' % rs, stdout=True)

    span(Yellow("In order to obtain the credential password/user we have to "
                "instantiate the credentials with a Local shell client\nwith "
                "PostgresSession(credential=credentials(shell).postgres, "
                "shell=shell, database='flsdb') as psql:"))
    with PostgresSession(database='flsdb') as psql:
        query = 'SELECT oid AS id, datname AS name, ' \
                'pg_database_size(datname) AS size FROM pg_database ' \
                'WHERE datistemplate = false ORDER BY name;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchall(query)
        log.debug('Result Set: %s\n' % rs, stdout=True)

        span(Green('Get all dbs: => psql.get_dbs()'))
        rs = psql.get_dbs()
        log.debug('psql.get_dbs(): %s\n' % rs, stdout=True)

        span(Green('Get all dbs: => psql.get_dbs(ignore_dbs=["template0", '
                   '"template1", "postgres"])'))
        rs = psql.get_dbs(ignore_dbs=['template0', 'template1', 'postgres'])
        log.debug('psql.get_dbs(): %s\n' % rs, stdout=True)


def demo_postgres_service(shell):
    box('Postgres Service Group')
    span(Yellow("Shell Environment => shell.os.env.type"))
    log.debug('Deployment Environment: %s' % shell.os.env.type,
              stdout=True)
    span(Yellow("shell.os.sg.pg"))
    log.debug('Service Group %s' % shell.os.sg.pg, stdout=True)

    span(Yellow("Postgres SG Members => shell.os.sg.pg.members"))
    log.debug('Postgres SG Members %s' % shell.os.sg.pg.members,
              stdout=True)

    span(Yellow("Postgres Constants: shell.os.sg.pg.consts"))
    log.debug('Postgres Host (deployment agnostic): %s' %
              shell.os.sg.pg.consts.pg_host, stdout=True)
    log.debug('Postgres Bin (deployment agnostic): %s' %
              shell.os.sg.pg.consts.pg_bin, stdout=True)
    log.debug('Postgres Mount (deployment agnostic): %s' %
              shell.os.sg.pg.consts.pg_mount, stdout=True)


def demo_shell_client(shell):
    box('Shell Demo')
    span(Yellow("Does a file exist => shell.os.fs.exists('/var/tmp')"))
    log.debug('Does /var/tmp exist: %s ' % shell.os.fs.exists('/var/tmp'),
              stdout=True)
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("make a dir => shell.os.fs.make_dirs('/var/tmp/test1')"))
    shell.os.fs.make_dirs('/var/tmp/test1')
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("Remove a dir => shell.os.fs.remove_dir('/var/tmp/test1')"))
    shell.os.fs.remove_dir('/var/tmp/test1')
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("Get the Size => shell.os.fs.get('/var/tmp/').size"))
    log.debug('Size of /var/tmp/ dir: %s ' %
              shell.os.fs.get('/var/tmp/').size, stdout=True)
    span(Blue("\nHeaps more functionality - check "
              "ERICdbpyu_CXP9039964/src/pyu/os/fs/filesystem.py"))


def demo_credentials(shell):
    box('Credentials')
    span(Yellow("shell.os.sg.pg.credentials_class"))
    log.debug('Service Group Credentials - Deployment agnostic %s' %
              shell.os.sg.pg.credentials_class, stdout=True)
    span(Yellow("Setup the Credentials => credentials."
                "setup(shell.os.sg.pg.credentials_class)"))
    credentials.setup(shell.os.sg.pg.credentials_class)
    span(Yellow("credential = credentials.postgres\ncreds = credential("
                "LocalShellClient())\n - use the localshell of vm"))
    credential = credentials.postgres
    creds = credential(LocalShellClient())
    span(Blue('unpack creds tuple => user, password = creds'))
    user, password = creds
    log.debug('Postgres user: %s & password %s' % (user, password),
              stdout=True)


def main():
    shell = LocalShellClient()
    # Very important to setup the logger in all main scripts
    log.setup_syslog('pglib_demo', verbose=True)
    credentials.setup(shell.os.sg.pg.credentials_class)

    demo_postgres_service(shell)
    demo_shell_client(shell)
    demo_credentials(shell)
    demo_local_psycopg_psql_session(shell)
    demo_local_psql_client(shell)


if __name__ == '__main__':
    main()
